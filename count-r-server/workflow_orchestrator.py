#!/usr/bin/env python3
"""
Workflow Orchestrator - Multi-step workflow management for MCP server
"""

import sys
import os
import time
import json
import asyncio
from typing import Dict, Any, List, Callable, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepStatus(Enum):
    """Individual step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    name: str
    description: str
    tool_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 30
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None  # Python expression for conditional execution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "validation_rules": self.validation_rules,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "depends_on": self.depends_on,
            "condition": self.condition
        }

@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance"""
    workflow_id: str
    workflow_name: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "status": self.status.value,
            "current_step": self.current_step,
            "results": self.results,
            "errors": self.errors,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metadata": self.metadata
        }

class WorkflowOrchestrator:
    """Main workflow orchestration engine"""
    
    def __init__(self, mcp_client=None):
        """Initialize the workflow orchestrator"""
        self.mcp_client = mcp_client
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.step_results: Dict[str, Dict[str, Any]] = {}
        
    def register_workflow(self, name: str, steps: List[WorkflowStep]) -> bool:
        """Register a new workflow"""
        try:
            # Validate workflow
            if not steps:
                logger.error(f"Workflow '{name}' must have at least one step")
                return False
                
            # Check for circular dependencies
            if self._has_circular_dependencies(steps):
                logger.error(f"Workflow '{name}' has circular dependencies")
                return False
                
            self.workflows[name] = steps
            logger.info(f"✅ Registered workflow: {name} with {len(steps)} steps")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register workflow '{name}': {e}")
            return False
    
    def _has_circular_dependencies(self, steps: List[WorkflowStep]) -> bool:
        """Check for circular dependencies in workflow steps"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_name: str) -> bool:
            if step_name in rec_stack:
                return True
            if step_name in visited:
                return False
                
            visited.add(step_name)
            rec_stack.add(step_name)
            
            # Find step by name
            step = next((s for s in steps if s.name == step_name), None)
            if step:
                for dep in step.depends_on:
                    if has_cycle(dep):
                        return True
                        
            rec_stack.remove(step_name)
            return False
        
        for step in steps:
            if has_cycle(step.name):
                return True
        return False
    
    def execute_workflow(self, workflow_name: str, initial_data: Dict[str, Any] = None) -> str:
        """Execute a workflow and return execution ID"""
        try:
            if workflow_name not in self.workflows:
                raise ValueError(f"Workflow '{workflow_name}' not found")
                
            workflow_id = f"{workflow_name}_{int(time.time())}"
            steps = self.workflows[workflow_name].copy()
            
            # Create execution instance
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                steps=steps,
                metadata=initial_data or {}
            )
            
            self.executions[workflow_id] = execution
            self.step_results[workflow_id] = {}
            
            # Start execution in background
            asyncio.create_task(self._execute_workflow_async(execution))
            
            logger.info(f"🚀 Started workflow execution: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"❌ Failed to start workflow '{workflow_name}': {e}")
            raise
    
    async def _execute_workflow_async(self, execution: WorkflowExecution):
        """Execute workflow asynchronously"""
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = datetime.now()
            
            # Execute steps in dependency order
            executed_steps = set()
            
            while len(executed_steps) < len(execution.steps):
                # Find steps ready to execute
                ready_steps = []
                for i, step in enumerate(execution.steps):
                    if step.name in executed_steps:
                        continue
                        
                    # Check dependencies
                    dependencies_met = all(dep in executed_steps for dep in step.depends_on)
                    if dependencies_met:
                        ready_steps.append((i, step))
                
                if not ready_steps:
                    # Deadlock or no ready steps
                    execution.status = WorkflowStatus.FAILED
                    execution.errors.append("No steps ready to execute - possible deadlock")
                    break
                
                # Execute ready steps
                for step_index, step in ready_steps:
                    try:
                        result = await self._execute_step(execution, step, step_index)
                        if result:
                            executed_steps.add(step.name)
                            execution.current_step = step_index + 1
                        else:
                            # Step failed
                            execution.status = WorkflowStatus.FAILED
                            execution.errors.append(f"Step '{step.name}' failed")
                            break
                            
                    except Exception as e:
                        execution.status = WorkflowStatus.FAILED
                        execution.errors.append(f"Step '{step.name}' error: {str(e)}")
                        break
            
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
                
            execution.end_time = datetime.now()
            logger.info(f"✅ Workflow execution completed: {execution.workflow_id} - {execution.status.value}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.errors.append(f"Workflow execution error: {str(e)}")
            execution.end_time = datetime.now()
            logger.error(f"❌ Workflow execution failed: {execution.workflow_id} - {e}")
    
    async def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep, step_index: int) -> bool:
        """Execute a single workflow step"""
        try:
            logger.info(f"🔄 Executing step: {step.name} ({step.tool_name})")
            
            # Check condition if specified
            if step.condition:
                if not self._evaluate_condition(step.condition, execution.results):
                    logger.info(f"⏭️ Skipping step '{step.name}' - condition not met")
                    return True
            
            # Prepare parameters with context
            params = self._prepare_parameters(step.parameters, execution.results)
            
            # Execute tool
            if self.mcp_client:
                result = await self._call_mcp_tool(step.tool_name, params, step.timeout)
            else:
                # Mock execution for testing
                result = {"status": "success", "data": f"Mock result for {step.name}"}
            
            # Validate result
            if self._validate_step_result(result, step.validation_rules):
                execution.results[step.name] = result
                self.step_results[execution.workflow_id][step.name] = result
                logger.info(f"✅ Step completed: {step.name}")
                return True
            else:
                logger.error(f"❌ Step validation failed: {step.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Step execution failed: {step.name} - {e}")
            return False
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression"""
        try:
            # Create a safe evaluation context
            safe_context = {
                'results': context,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict
            }
            return eval(condition, {"__builtins__": {}}, safe_context)
        except Exception as e:
            logger.error(f"❌ Condition evaluation failed: {condition} - {e}")
            return False
    
    def _prepare_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare step parameters with context substitution"""
        prepared = {}
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Template substitution
                var_name = value[2:-2].strip()
                if var_name in context:
                    prepared[key] = context[var_name]
                else:
                    prepared[key] = value
            else:
                prepared[key] = value
        return prepared
    
    async def _call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        """Call MCP tool with timeout"""
        try:
            # This would be implemented based on your MCP client
            # For now, return a mock result
            return {
                "status": "success",
                "tool": tool_name,
                "parameters": parameters,
                "result": f"Mock result for {tool_name}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _validate_step_result(self, result: Dict[str, Any], rules: Dict[str, Any]) -> bool:
        """Validate step result against rules"""
        if not rules:
            return True
            
        try:
            # Check required fields
            if "required_fields" in rules:
                for field in rules["required_fields"]:
                    if field not in result:
                        return False
            
            # Check status
            if "expected_status" in rules:
                if result.get("status") != rules["expected_status"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Result validation error: {e}")
            return False
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status and results"""
        if execution_id not in self.executions:
            return None
            
        execution = self.executions[execution_id]
        return execution.to_dict()
    
    def get_all_executions(self) -> List[Dict[str, Any]]:
        """Get all workflow executions"""
        return [execution.to_dict() for execution in self.executions.values()]
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution"""
        if execution_id not in self.executions:
            return False
            
        execution = self.executions[execution_id]
        if execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.now()
            logger.info(f"🛑 Cancelled workflow execution: {execution_id}")
            return True
            
        return False

# Predefined workflow templates
class WorkflowTemplates:
    """Collection of predefined workflow templates"""
    
    @staticmethod
    def data_processing_workflow() -> List[WorkflowStep]:
        """Example: Fetch data → Validate → Summarize → Notify user"""
        return [
            WorkflowStep(
                name="fetch_data",
                description="Fetch data from source",
                tool_name="list_desktop_contents",
                parameters={},
                validation_rules={"required_fields": ["status"]}
            ),
            WorkflowStep(
                name="validate_data",
                description="Validate fetched data",
                tool_name="count_r",
                parameters={"word": "{{fetch_data.result}}" if "fetch_data" else "test"},
                depends_on=["fetch_data"],
                validation_rules={"expected_status": "success"}
            ),
            WorkflowStep(
                name="summarize_data",
                description="Create summary of validated data",
                tool_name="get_desktop_path",
                parameters={},
                depends_on=["validate_data"],
                condition="len(results.get('validate_data', {}).get('result', '')) > 0"
            ),
            WorkflowStep(
                name="notify_user",
                description="Send notification to user",
                tool_name="open_gmail",
                parameters={},
                depends_on=["summarize_data"],
                condition="results.get('summarize_data', {}).get('status') == 'success'"
            )
        ]
    
    @staticmethod
    def email_campaign_workflow() -> List[WorkflowStep]:
        """Email campaign workflow"""
        return [
            WorkflowStep(
                name="prepare_recipients",
                description="Prepare email recipient list",
                tool_name="list_desktop_contents",
                parameters={},
                validation_rules={"required_fields": ["status"]}
            ),
            WorkflowStep(
                name="validate_emails",
                description="Validate email addresses",
                tool_name="count_r",
                parameters={"word": "{{prepare_recipients.result}}" if "prepare_recipients" else "test"},
                depends_on=["prepare_recipients"]
            ),
            WorkflowStep(
                name="send_emails",
                description="Send emails to validated recipients",
                tool_name="sendmail_simple",
                parameters={
                    "to_email": "test@example.com",
                    "subject": "Campaign Email",
                    "message": "This is a campaign email."
                },
                depends_on=["validate_emails"],
                condition="results.get('validate_emails', {}).get('status') == 'success'"
            ),
            WorkflowStep(
                name="confirm_delivery",
                description="Confirm email delivery",
                tool_name="open_gmail",
                parameters={},
                depends_on=["send_emails"]
            )
        ]
    
    @staticmethod
    def file_analysis_workflow() -> List[WorkflowStep]:
        """File analysis workflow"""
        return [
            WorkflowStep(
                name="scan_directory",
                description="Scan directory for files",
                tool_name="list_desktop_contents",
                parameters={},
                validation_rules={"required_fields": ["status"]}
            ),
            WorkflowStep(
                name="analyze_files",
                description="Analyze found files",
                tool_name="count_r",
                parameters={"word": "{{scan_directory.result}}" if "scan_directory" else "files"},
                depends_on=["scan_directory"]
            ),
            WorkflowStep(
                name="generate_report",
                description="Generate analysis report",
                tool_name="get_desktop_path",
                parameters={},
                depends_on=["analyze_files"]
            ),
            WorkflowStep(
                name="save_report",
                description="Save report to desktop",
                tool_name="open_gmail_compose",
                parameters={},
                depends_on=["generate_report"]
            )
        ]

# Global orchestrator instance
orchestrator = WorkflowOrchestrator()

def register_default_workflows():
    """Register default workflow templates"""
    orchestrator.register_workflow("data_processing", WorkflowTemplates.data_processing_workflow())
    orchestrator.register_workflow("email_campaign", WorkflowTemplates.email_campaign_workflow())
    orchestrator.register_workflow("file_analysis", WorkflowTemplates.file_analysis_workflow())
    logger.info("✅ Registered default workflow templates")

if __name__ == "__main__":
    # Test the workflow orchestrator
    register_default_workflows()
    print("🔧 Workflow Orchestrator initialized with default templates") 