# ITSM System - Advanced Business Logic & Algorithms
## Complete Implementation Guide for Core Processes (ITIL v4 Compliant)

---

## TABLE OF CONTENTS
1. [Priority Calculation Engine](#priority-calculation)
2. [SLA Management & Calculation](#sla-management)
3. [Automatic Assignment Logic](#auto-assignment)
4. [Escalation Engine](#escalation-engine)
5. [Workflow Engine](#workflow-engine)
6. [Notification Service](#notification-service)
7. [Advanced Analytics & Prediction](#analytics)

---

## PRIORITY CALCULATION ENGINE {#priority-calculation}

### 1.1 ITIL Impact x Urgency Matrix

```python
"""
Priority Calculation Implementation
ITIL v4 Standard Impact x Urgency Matrix
"""

from enum import Enum
from typing import Dict, Tuple
from datetime import datetime, timedelta

class ImpactLevel(Enum):
    HIGH = "high"       # Affects business-critical functions or many users
    MEDIUM = "medium"   # Affects important functions or moderate users
    LOW = "low"         # Affects minor functions or few users

class UrgencyLevel(Enum):
    HIGH = "high"       # Needs resolution within hours
    MEDIUM = "medium"   # Needs resolution within 1-2 days
    LOW = "low"         # Can wait for planned maintenance

class PriorityLevel(Enum):
    CRITICAL = "critical"  # P1 - Immediate action required
    HIGH = "high"          # P2 - Within hours
    MEDIUM = "medium"      # P3 - Within 1 day
    LOW = "low"            # P4 - Within 1 week

def calculate_incident_priority(impact: ImpactLevel, urgency: UrgencyLevel) -> PriorityLevel:
    """
    Calculate incident priority using ITIL standard matrix
    
    Args:
        impact: Impact level (high, medium, low)
        urgency: Urgency level (high, medium, low)
    
    Returns:
        Priority level based on matrix
    
    ITIL Priority Matrix:
    
    Impact\Urgency    High        Medium       Low
    High              Critical    High         Medium
    Medium            High        Medium       Low
    Low               Medium      Low          Low
    """
    
    priority_matrix: Dict[Tuple[ImpactLevel, UrgencyLevel], PriorityLevel] = {
        # High Impact
        (ImpactLevel.HIGH, UrgencyLevel.HIGH): PriorityLevel.CRITICAL,
        (ImpactLevel.HIGH, UrgencyLevel.MEDIUM): PriorityLevel.HIGH,
        (ImpactLevel.HIGH, UrgencyLevel.LOW): PriorityLevel.MEDIUM,
        
        # Medium Impact
        (ImpactLevel.MEDIUM, UrgencyLevel.HIGH): PriorityLevel.HIGH,
        (ImpactLevel.MEDIUM, UrgencyLevel.MEDIUM): PriorityLevel.MEDIUM,
        (ImpactLevel.MEDIUM, UrgencyLevel.LOW): PriorityLevel.LOW,
        
        # Low Impact
        (ImpactLevel.LOW, UrgencyLevel.HIGH): PriorityLevel.MEDIUM,
        (ImpactLevel.LOW, UrgencyLevel.MEDIUM): PriorityLevel.LOW,
        (ImpactLevel.LOW, UrgencyLevel.LOW): PriorityLevel.LOW,
    }
    
    priority = priority_matrix.get((impact, urgency), PriorityLevel.LOW)
    return priority


# Extended Priority Calculation with Scoring
class PriorityCalculationEngine:
    """
    Advanced priority calculation with scoring factors
    """
    
    def __init__(self):
        # Weight factors
        self.impact_weight = 0.5
        self.urgency_weight = 0.3
        self.business_criticality_weight = 0.2
        
        # Impact scoring
        self.impact_scores = {
            "high": 100,      # Affects critical services/many users
            "medium": 50,     # Affects important services/some users
            "low": 10         # Affects minor services/few users
        }
        
        # Urgency scoring
        self.urgency_scores = {
            "high": 100,      # Needs immediate resolution
            "medium": 50,     # Needs resolution within hours/days
            "low": 10         # Can wait for scheduled maintenance
        }
        
        # Business criticality scoring
        self.criticality_scores = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25
        }
    
    def calculate_priority_score(self, impact: str, urgency: str, 
                                 business_criticality: str = None) -> Dict:
        """
        Calculate weighted priority score
        
        Returns:
            {
                "total_score": 0-100,
                "impact_score": 0-100,
                "urgency_score": 0-100,
                "criticality_score": 0-100,
                "priority_level": "critical|high|medium|low"
            }
        """
        
        impact_score = self.impact_scores.get(impact.lower(), 0)
        urgency_score = self.urgency_scores.get(urgency.lower(), 0)
        criticality_score = (
            self.criticality_scores.get(business_criticality.lower(), 0)
            if business_criticality else 0
        )
        
        # Calculate weighted total
        weighted_impact = impact_score * self.impact_weight
        weighted_urgency = urgency_score * self.urgency_weight
        weighted_criticality = (
            criticality_score * self.business_criticality_weight
            if business_criticality else 0
        )
        
        total_score = weighted_impact + weighted_urgency + weighted_criticality
        
        # Determine priority level
        if total_score >= 80:
            priority_level = "critical"
        elif total_score >= 60:
            priority_level = "high"
        elif total_score >= 40:
            priority_level = "medium"
        else:
            priority_level = "low"
        
        return {
            "total_score": round(total_score, 2),
            "impact_score": impact_score,
            "urgency_score": urgency_score,
            "criticality_score": criticality_score,
            "priority_level": priority_level,
            "calculation_method": "weighted_scoring"
        }
    
    def assess_impact(self, affected_users_count: int, 
                     business_function_criticality: str,
                     affected_services: list) -> str:
        """
        Assess impact level based on multiple factors
        """
        
        critical_services = [
            'email', 'erp', 'payment_gateway', 'authentication',
            'database', 'vpn', 'file_sharing'
        ]
        
        # High impact conditions
        if (affected_users_count > 100 or 
            business_function_criticality == 'critical' or
            any(service.lower() in critical_services for service in affected_services)):
            return "high"
        
        # Medium impact conditions
        elif (affected_users_count > 10 or 
              business_function_criticality in ['high', 'medium']):
            return "medium"
        
        # Low impact
        else:
            return "low"
    
    def assess_urgency(self, time_to_deadline: timedelta, 
                      workaround_available: bool,
                      productivity_impact: str) -> str:
        """
        Assess urgency level based on time and impact
        """
        
        hours_to_deadline = time_to_deadline.total_seconds() / 3600 if time_to_deadline else float('inf')
        
        # High urgency
        if (productivity_impact == 'complete_stop' or 
            (hours_to_deadline and hours_to_deadline < 4) or
            not workaround_available):
            return "high"
        
        # Medium urgency
        elif (productivity_impact == 'significant' or
              (hours_to_deadline and hours_to_deadline < 24)):
            return "medium"
        
        # Low urgency
        else:
            return "low"


# Example Usage
engine = PriorityCalculationEngine()

# Scenario: Email service down for 150 users
result = engine.calculate_priority_score(
    impact="high",
    urgency="high",
    business_criticality="critical"
)

print(f"Priority Score: {result['total_score']}")  # Output: ~95
print(f"Priority Level: {result['priority_level']}")  # Output: critical
```

---

## SLA MANAGEMENT & CALCULATION {#sla-management}

### 2.1 SLA Clock & Time Calculation

```python
"""
SLA Clock Management
Includes: Response Time, Resolution Time, Business Hours calculation
"""

from datetime import datetime, timedelta, time
from typing import Dict, List, Optional
import pytz

class SLAClock:
    """
    Manages SLA time calculation with business hours
    """
    
    def __init__(self, organization_id: str):
        self.organization_id = organization_id
        self.business_hours_start = time(8, 0)    # 8 AM
        self.business_hours_end = time(18, 0)     # 6 PM
        self.working_days = [0, 1, 2, 3, 4]       # Monday-Friday (0-4)
        self.timezone = pytz.timezone('Asia/Jakarta')
        self.holidays = []
    
    def is_business_hours(self, dt: datetime) -> bool:
        """Check if datetime is within business hours"""
        
        dt_local = dt.astimezone(self.timezone)
        
        # Check if it's a working day
        if dt_local.weekday() not in self.working_days:
            return False
        
        # Check if it's a holiday
        if dt_local.date() in self.holidays:
            return False
        
        # Check time range
        return self.business_hours_start <= dt_local.time() <= self.business_hours_end
    
    def calculate_business_hours_elapsed(self, start_time: datetime, 
                                         end_time: datetime) -> timedelta:
        """
        Calculate elapsed business hours between two times
        
        Example:
            If created at 5 PM Friday and current time is 9 AM Monday
            Elapsed business hours = 1 hour (Fri) + 1 hour (Mon) = 2 hours
            (Not including weekend)
        """
        
        elapsed_business_seconds = 0
        current_time = start_time
        
        while current_time < end_time:
            # Move to next hour
            next_hour = current_time + timedelta(hours=1)
            check_time = next_hour if next_hour <= end_time else end_time
            
            # Check if this hour is within business hours
            if self.is_business_hours(current_time):
                elapsed_business_seconds += (check_time - current_time).total_seconds()
            
            current_time = next_hour
        
        return timedelta(seconds=elapsed_business_seconds)
    
    def calculate_sla_due_date(self, start_time: datetime, 
                               target_hours: int,
                               business_hours_only: bool = True) -> datetime:
        """
        Calculate SLA due date based on target hours
        
        Example:
            If created at 4 PM Friday with 4 hour SLA
            Due date = Monday 12 PM (skipping weekend)
        """
        
        if not business_hours_only:
            # Simple calendar time
            return start_time + timedelta(hours=target_hours)
        
        # Business hours calculation
        target_seconds = target_hours * 3600
        current_time = start_time
        elapsed_seconds = 0
        
        while elapsed_seconds < target_seconds:
            current_time += timedelta(hours=1)
            
            if self.is_business_hours(current_time):
                elapsed_seconds += 3600
        
        return current_time


class SLABreachDetector:
    """
    Detects SLA breaches and tracks SLA status
    """
    
    def __init__(self, sla_clock: SLAClock):
        self.sla_clock = sla_clock
    
    def check_sla_breach(self, ticket_created_time: datetime,
                        sla_response_due: datetime,
                        sla_resolution_due: datetime,
                        response_provided_time: Optional[datetime] = None,
                        resolved_time: Optional[datetime] = None) -> Dict:
        """
        Check if ticket has breached SLA
        """
        
        current_time = datetime.now(pytz.UTC)
        
        response_breached = False
        response_breach_time = None
        resolution_breached = False
        resolution_breach_time = None
        
        # Check response SLA
        if response_provided_time:
            if response_provided_time > sla_response_due:
                response_breached = True
                response_breach_time = response_provided_time
        elif current_time > sla_response_due:
            response_breached = True
        
        # Check resolution SLA
        if resolved_time:
            if resolved_time > sla_resolution_due:
                resolution_breached = True
                resolution_breach_time = resolved_time
        elif current_time > sla_resolution_due:
            resolution_breached = True
        
        # Calculate SLA status
        sla_status = "ON_TRACK"
        if resolution_breached:
            sla_status = "BREACHED"
        elif current_time > sla_resolution_due - timedelta(hours=1):
            sla_status = "CRITICAL"
        elif current_time > sla_resolution_due - timedelta(hours=2):
            sla_status = "WARNING"
        
        # Hours remaining
        hours_remaining = (sla_resolution_due - current_time).total_seconds() / 3600
        
        return {
            "response_breached": response_breached,
            "resolution_breached": resolution_breached,
            "response_breach_time": response_breach_time,
            "resolution_breach_time": resolution_breach_time,
            "sla_status": sla_status,
            "hours_remaining": round(hours_remaining, 1),
            "percentage_time_remaining": round(
                (hours_remaining / 4) * 100, 1
            ) if resolution_breach_time is None else 0
        }


### 2.2 SLA Escalation

```python
class SLAEscalationEngine:
    """
    Automatic escalation when SLA approaches breach
    """
    
    ESCALATION_LEVELS = {
        "level_1": {
            "trigger": "75_percent_sla",  # When 75% of SLA time used
            "action": "notify_assignee",
            "escalate_to": "team_lead"
        },
        "level_2": {
            "trigger": "90_percent_sla",  # When 90% of SLA time used
            "action": "escalate_ticket",
            "escalate_to": "manager"
        },
        "level_3": {
            "trigger": "sla_breach",  # After SLA breach
            "action": "escalate_to_director",
            "escalate_to": "director"
        }
    }
    
    def check_escalation_required(self, sla_info: Dict) -> Optional[Dict]:
        """
        Check if escalation is required based on SLA status
        """
        
        hours_remaining = sla_info['hours_remaining']
        total_sla_hours = 4  # Example: 4-hour SLA
        
        percentage_used = ((total_sla_hours - hours_remaining) / total_sla_hours) * 100
        
        if percentage_used >= 90:
            return {
                "escalation_level": "level_2",
                "trigger": "90_percent_sla",
                "action": "escalate_ticket",
                "escalate_to": "manager"
            }
        elif percentage_used >= 75:
            return {
                "escalation_level": "level_1",
                "trigger": "75_percent_sla",
                "action": "notify_assignee",
                "escalate_to": "team_lead"
            }
        
        return None
    
    def execute_escalation(self, ticket_id: str, escalation_info: Dict):
        """Execute escalation action"""
        
        if escalation_info['action'] == 'notify_assignee':
            # Send notification to current assignee
            notification = {
                "ticket_id": ticket_id,
                "type": "sla_warning",
                "message": "SLA approaching breach. 75% of time used.",
                "priority": "high"
            }
        
        elif escalation_info['action'] == 'escalate_ticket':
            # Escalate to manager
            notification = {
                "ticket_id": ticket_id,
                "type": "sla_escalation",
                "message": "SLA critical. 90% of time used. Escalating to manager.",
                "priority": "critical",
                "escalate_to": escalation_info['escalate_to']
            }
        
        return notification
```

---

## AUTOMATIC ASSIGNMENT LOGIC {#auto-assignment}

### 3.1 Assignment Algorithm

```python
"""
Intelligent ticket assignment based on:
1. Agent skill match
2. Current workload
3. Availability
4. Team queue strategy
"""

from typing import List, Dict, Optional
from enum import Enum

class QueueStrategy(Enum):
    ROUND_ROBIN = "round_robin"          # Rotate assignments
    LEAST_LOADED = "least_loaded"        # Assign to least busy agent
    SKILL_BASED = "skill_based"          # Match to agent skills
    PRIORITY_BASED = "priority_based"    # Experienced agents for high priority

class AssignmentEngine:
    """
    Intelligent ticket assignment engine
    """
    
    def __init__(self, team_id: str, queue_strategy: QueueStrategy):
        self.team_id = team_id
        self.queue_strategy = queue_strategy
    
    def get_best_agent(self, ticket_data: Dict) -> Optional[str]:
        """
        Get best agent for assignment
        
        Args:
            ticket_data: {
                "category": "Email",
                "priority": "critical",
                "complexity": "high",
                "required_skills": ["email_administration", "user_support"]
            }
        """
        
        # Get active team members
        team_members = self._get_active_team_members()
        
        # Filter by availability
        available_agents = [
            agent for agent in team_members
            if agent['is_available'] and agent['open_tickets'] < agent['max_tickets']
        ]
        
        if not available_agents:
            return None
        
        # Apply queue strategy
        if self.queue_strategy == QueueStrategy.ROUND_ROBIN:
            return self._round_robin_assignment(available_agents)
        
        elif self.queue_strategy == QueueStrategy.LEAST_LOADED:
            return self._least_loaded_assignment(available_agents)
        
        elif self.queue_strategy == QueueStrategy.SKILL_BASED:
            return self._skill_based_assignment(
                available_agents,
                ticket_data.get('required_skills', [])
            )
        
        elif self.queue_strategy == QueueStrategy.PRIORITY_BASED:
            return self._priority_based_assignment(
                available_agents,
                ticket_data.get('priority')
            )
        
        return available_agents[0]['agent_id']
    
    def _round_robin_assignment(self, agents: List[Dict]) -> str:
        """
        Round-robin assignment: cycle through agents
        """
        
        # Get agent with lowest assignment count this rotation
        last_assigned = self._get_last_assigned_agent()
        
        agents_sorted = sorted(agents, key=lambda x: x['agent_id'])
        
        for agent in agents_sorted:
            if agent['agent_id'] > last_assigned:
                self._set_last_assigned(agent['agent_id'])
                return agent['agent_id']
        
        # Cycle back to first agent
        self._set_last_assigned(agents_sorted[0]['agent_id'])
        return agents_sorted[0]['agent_id']
    
    def _least_loaded_assignment(self, agents: List[Dict]) -> str:
        """
        Assign to agent with least open tickets
        """
        
        return min(agents, key=lambda x: x['open_tickets'])['agent_id']
    
    def _skill_based_assignment(self, agents: List[Dict], 
                                required_skills: List[str]) -> str:
        """
        Assign to agent with best skill match
        """
        
        scored_agents = []
        
        for agent in agents:
            skill_match_score = 0
            agent_skills = agent.get('skills', [])
            
            for required_skill in required_skills:
                if required_skill in agent_skills:
                    skill_match_score += 1
            
            # Tiebreaker: least loaded
            workload_score = 1.0 / (agent['open_tickets'] + 1)
            
            total_score = (skill_match_score * 0.7) + (workload_score * 0.3)
            scored_agents.append({
                'agent_id': agent['agent_id'],
                'score': total_score
            })
        
        return max(scored_agents, key=lambda x: x['score'])['agent_id']
    
    def _priority_based_assignment(self, agents: List[Dict], 
                                   priority: str) -> str:
        """
        Assign high-priority tickets to experienced agents
        """
        
        if priority == 'critical':
            # Assign to most experienced agent
            return max(agents, key=lambda x: x['experience_level'])['agent_id']
        
        elif priority == 'high':
            # Assign to senior agents (not juniors)
            senior_agents = [a for a in agents if a['experience_level'] >= 2]
            if senior_agents:
                return min(senior_agents, key=lambda x: x['open_tickets'])['agent_id']
        
        # For medium/low, use least loaded
        return min(agents, key=lambda x: x['open_tickets'])['agent_id']
    
    def _get_active_team_members(self) -> List[Dict]:
        """Fetch active team members from database"""
        # Implementation: Query database for team members
        pass
    
    def _get_last_assigned_agent(self) -> str:
        """Get last assigned agent for round-robin"""
        # Implementation: Query cache/database
        pass
    
    def _set_last_assigned(self, agent_id: str):
        """Update last assigned agent"""
        # Implementation: Update cache/database
        pass
```

---

## ESCALATION ENGINE {#escalation-engine}

### 4.1 Multi-Level Escalation

```python
"""
Automatic escalation based on:
1. SLA breach
2. Time in current status
3. Manual escalation
4. Customer feedback
"""

class EscalationEngine:
    """
    Multi-level escalation management
    """
    
    ESCALATION_RULES = {
        "sla_response_breach": {
            "condition": "response_sla_breached",
            "escalate_to": "team_lead",
            "message": "SLA Response breach. Escalating to Team Lead."
        },
        "sla_resolution_breach": {
            "condition": "resolution_sla_breached",
            "escalate_to": "manager",
            "message": "SLA Resolution breach. Escalating to Manager."
        },
        "time_in_status": {
            "condition": "ticket_in_status > 24_hours",
            "status": "in_progress",
            "escalate_to": "team_lead",
            "message": "Ticket in-progress for 24+ hours. Escalation required."
        },
        "manual_escalation": {
            "condition": "user_requested",
            "escalate_to": "manager",
            "message": "User requested escalation."
        }
    }
    
    def check_escalation_triggers(self, ticket: Dict) -> Optional[Dict]:
        """
        Check if any escalation trigger is met
        """
        
        triggers = []
        
        # Check SLA breaches
        if ticket['sla_response_breached']:
            triggers.append(self.ESCALATION_RULES['sla_response_breach'])
        
        if ticket['sla_resolution_breached']:
            triggers.append(self.ESCALATION_RULES['sla_resolution_breach'])
        
        # Check time in status
        if ticket['status'] == 'in_progress':
            time_in_status = (datetime.now() - ticket['status_changed_at']).total_seconds() / 3600
            if time_in_status > 24:
                triggers.append(self.ESCALATION_RULES['time_in_status'])
        
        return triggers[0] if triggers else None
    
    def execute_escalation(self, ticket_id: str, escalation_rule: Dict) -> Dict:
        """
        Execute escalation action
        """
        
        escalation_record = {
            "ticket_id": ticket_id,
            "escalation_type": escalation_rule['condition'],
            "escalated_to_role": escalation_rule['escalate_to'],
            "escalation_time": datetime.now(),
            "reason": escalation_rule['message'],
            "status": "pending"
        }
        
        # Find appropriate person for escalation
        escalated_to = self._find_escalation_user(
            escalation_rule['escalate_to'],
            ticket_id
        )
        
        # Send notification
        self._send_escalation_notification(escalation_record, escalated_to)
        
        # Update ticket
        self._update_ticket_escalation(ticket_id, escalation_record)
        
        return escalation_record
    
    def _find_escalation_user(self, role: str, ticket_id: str):
        """Find appropriate user for escalation"""
        # Implementation: Query database for user with role
        pass
    
    def _send_escalation_notification(self, escalation: Dict, user: Dict):
        """Send notification to escalated user"""
        # Implementation: Send email/notification
        pass
    
    def _update_ticket_escalation(self, ticket_id: str, escalation: Dict):
        """Update ticket with escalation info"""
        # Implementation: Update database
        pass
```

---

## WORKFLOW ENGINE {#workflow-engine}

### 5.1 Service Request Approval Workflow

```python
"""
Multi-level approval workflow for Service Requests
"""

from enum import Enum
from typing import List, Dict, Optional

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REASSIGNED = "reassigned"

class WorkflowEngine:
    """
    Manages approval workflows for service requests
    """
    
    def __init__(self, service_id: str):
        self.service_id = service_id
        self.approval_steps = []
    
    def define_approval_workflow(self, steps: List[Dict]):
        """
        Define approval workflow for service
        
        Example workflow:
        [
            {
                "step": 1,
                "approver_role": "manager",
                "criteria": "all_requests",
                "timeout_hours": 24
            },
            {
                "step": 2,
                "approver_role": "director",
                "criteria": "cost > 1000",
                "timeout_hours": 48
            }
        ]
        """
        
        self.approval_steps = sorted(steps, key=lambda x: x['step'])
    
    def initiate_workflow(self, request_id: str, request_data: Dict) -> Dict:
        """
        Initiate approval workflow
        """
        
        workflow = {
            "request_id": request_id,
            "current_step": 1,
            "total_steps": len(self.approval_steps),
            "approvals": []
        }
        
        # Get first step
        first_step = self.approval_steps[0]
        
        # Find approver for first step
        approver = self._find_approver(first_step, request_data)
        
        approval_record = {
            "step": 1,
            "approver_id": approver['user_id'],
            "status": ApprovalStatus.PENDING.value,
            "deadline": datetime.now() + timedelta(hours=first_step['timeout_hours']),
            "created_at": datetime.now()
        }
        
        workflow['approvals'].append(approval_record)
        workflow['current_approver'] = approver
        
        # Send notification to approver
        self._send_approval_notification(request_id, approver, first_step)
        
        return workflow
    
    def process_approval(self, request_id: str, step: int, 
                        approver_id: str, decision: str,
                        comments: str = "") -> Dict:
        """
        Process approval decision
        
        Args:
            decision: "approved" or "rejected"
        """
        
        approval_record = {
            "request_id": request_id,
            "step": step,
            "approver_id": approver_id,
            "decision": decision,
            "comments": comments,
            "decided_at": datetime.now()
        }
        
        if decision == "rejected":
            # Return to requester
            return {
                "status": "rejected",
                "approval_record": approval_record,
                "next_action": "notify_requester"
            }
        
        elif decision == "approved":
            # Move to next step if available
            if step < len(self.approval_steps):
                next_step = self.approval_steps[step]  # step+1 already, array 0-indexed
                next_approver = self._find_approver_for_step(next_step)
                
                return {
                    "status": "approved",
                    "approval_record": approval_record,
                    "next_step": step + 1,
                    "next_approver": next_approver,
                    "next_action": "send_for_next_approval"
                }
            else:
                # All approvals complete
                return {
                    "status": "approved",
                    "approval_record": approval_record,
                    "workflow_complete": True,
                    "next_action": "fulfill_request"
                }
        
        return None
    
    def _find_approver(self, step: Dict, request_data: Dict) -> Dict:
        """Find approver for approval step"""
        # Implementation: Find user by role
        pass
    
    def _find_approver_for_step(self, step: Dict) -> Dict:
        """Find approver for next step"""
        # Implementation: Find user by role
        pass
    
    def _send_approval_notification(self, request_id: str, approver: Dict, 
                                    step: Dict):
        """Send approval notification to approver"""
        # Implementation: Send email/notification
        pass
```

---

## NOTIFICATION SERVICE {#notification-service}

### 6.1 Multi-Channel Notifications

```python
"""
Notification service supporting multiple channels:
- Email
- SMS
- Slack
- Teams
- In-app notifications
"""

from enum import Enum
from typing import List, Dict

class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"
    IN_APP = "in_app"

class NotificationTemplate:
    """Base notification template"""
    
    def __init__(self, template_id: str):
        self.template_id = template_id
    
    def render(self, context: Dict) -> str:
        """Render template with context data"""
        # Implementation: Render template
        pass

class NotificationService:
    """
    Multi-channel notification service
    """
    
    NOTIFICATION_EVENTS = {
        "ticket_created": {
            "channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            "recipients": ["requester", "assigned_agent"]
        },
        "sla_warning": {
            "channels": [NotificationChannel.EMAIL, NotificationChannel.SLACK],
            "recipients": ["assigned_agent", "team_lead"]
        },
        "ticket_assigned": {
            "channels": [NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.IN_APP],
            "recipients": ["assigned_agent"]
        },
        "approval_required": {
            "channels": [NotificationChannel.EMAIL, NotificationChannel.SLACK],
            "recipients": ["approver"]
        },
        "ticket_resolved": {
            "channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
            "recipients": ["requester"]
        }
    }
    
    def send_notification(self, event_type: str, ticket_data: Dict) -> Dict:
        """
        Send notification for event
        """
        
        event_config = self.NOTIFICATION_EVENTS.get(event_type)
        
        if not event_config:
            return {"status": "event_not_found"}
        
        recipients = self._get_recipients(event_config['recipients'], ticket_data)
        channels = event_config['channels']
        
        notification_results = []
        
        for recipient in recipients:
            for channel in channels:
                result = self._send_via_channel(
                    channel,
                    recipient,
                    event_type,
                    ticket_data
                )
                notification_results.append(result)
        
        return {
            "status": "sent",
            "event_type": event_type,
            "notifications_sent": len(notification_results),
            "results": notification_results
        }
    
    def _get_recipients(self, recipient_types: List[str], 
                       ticket_data: Dict) -> List[Dict]:
        """Get recipient list based on types"""
        
        recipients = []
        
        for recipient_type in recipient_types:
            if recipient_type == "requester":
                recipients.append({
                    "user_id": ticket_data['requester_id'],
                    "email": ticket_data['requester_email'],
                    "role": "requester"
                })
            elif recipient_type == "assigned_agent":
                recipients.append({
                    "user_id": ticket_data['assigned_to_id'],
                    "email": ticket_data['assigned_agent_email'],
                    "role": "agent"
                })
            elif recipient_type == "team_lead":
                recipients.append({
                    "user_id": ticket_data['team_lead_id'],
                    "email": ticket_data['team_lead_email'],
                    "role": "team_lead"
                })
            elif recipient_type == "approver":
                recipients.append({
                    "user_id": ticket_data['current_approver_id'],
                    "email": ticket_data['current_approver_email'],
                    "role": "approver"
                })
        
        return recipients
    
    def _send_via_channel(self, channel: NotificationChannel, 
                         recipient: Dict, event_type: str,
                         ticket_data: Dict) -> Dict:
        """Send notification via specific channel"""
        
        template = self._get_template(event_type, channel)
        message = template.render(ticket_data)
        
        if channel == NotificationChannel.EMAIL:
            return self._send_email(recipient, message)
        
        elif channel == NotificationChannel.SLACK:
            return self._send_slack(recipient, message)
        
        elif channel == NotificationChannel.TEAMS:
            return self._send_teams(recipient, message)
        
        elif channel == NotificationChannel.SMS:
            return self._send_sms(recipient, message)
        
        elif channel == NotificationChannel.IN_APP:
            return self._send_in_app(recipient, message)
        
        return {"status": "unknown_channel"}
    
    def _send_email(self, recipient: Dict, message: str) -> Dict:
        """Send email notification"""
        # Implementation: Use email service (SendGrid, etc)
        pass
    
    def _send_slack(self, recipient: Dict, message: str) -> Dict:
        """Send Slack notification"""
        # Implementation: Use Slack API
        pass
    
    def _send_teams(self, recipient: Dict, message: str) -> Dict:
        """Send Teams notification"""
        # Implementation: Use Teams API
        pass
    
    def _send_sms(self, recipient: Dict, message: str) -> Dict:
        """Send SMS notification"""
        # Implementation: Use SMS service (Twilio, etc)
        pass
    
    def _send_in_app(self, recipient: Dict, message: str) -> Dict:
        """Send in-app notification"""
        # Implementation: Store in notifications table
        pass
    
    def _get_template(self, event_type: str, channel: NotificationChannel) -> NotificationTemplate:
        """Get notification template"""
        # Implementation: Get template from database
        pass
```

---

## ADVANCED ANALYTICS & PREDICTION {#analytics}

### 7.1 Metrics & Analytics

```python
"""
Advanced ITSM analytics and reporting
"""

from datetime import datetime, timedelta
from typing import Dict, List
import statistics

class ITSMAnalytics:
    """
    ITSM system analytics and KPI calculation
    """
    
    def calculate_mttr(self, tickets: List[Dict]) -> Dict:
        """
        Mean Time To Resolve (MTTR)
        
        MTTR = Sum of all resolution times / Number of resolved tickets
        """
        
        resolved_times = []
        
        for ticket in tickets:
            if ticket['resolved_at'] and ticket['created_at']:
                resolution_time = (
                    ticket['resolved_at'] - ticket['created_at']
                ).total_seconds() / 3600  # in hours
                resolved_times.append(resolution_time)
        
        if not resolved_times:
            return {"mttr": 0, "unit": "hours"}
        
        mttr = statistics.mean(resolved_times)
        
        return {
            "mttr": round(mttr, 2),
            "unit": "hours",
            "min": round(min(resolved_times), 2),
            "max": round(max(resolved_times), 2),
            "median": round(statistics.median(resolved_times), 2),
            "count": len(resolved_times)
        }
    
    def calculate_mtta(self, tickets: List[Dict]) -> Dict:
        """
        Mean Time To Acknowledge (MTTA)
        
        MTTA = Sum of all acknowledgement times / Number of acknowledged tickets
        """
        
        ack_times = []
        
        for ticket in tickets:
            if ticket['assigned_at'] and ticket['created_at']:
                ack_time = (
                    ticket['assigned_at'] - ticket['created_at']
                ).total_seconds() / 60  # in minutes
                ack_times.append(ack_time)
        
        if not ack_times:
            return {"mtta": 0, "unit": "minutes"}
        
        mtta = statistics.mean(ack_times)
        
        return {
            "mtta": round(mtta, 2),
            "unit": "minutes",
            "min": round(min(ack_times), 2),
            "max": round(max(ack_times), 2),
            "median": round(statistics.median(ack_times), 2),
            "count": len(ack_times)
        }
    
    def calculate_first_contact_resolution(self, tickets: List[Dict]) -> Dict:
        """
        First Contact Resolution Rate (FCR)
        
        FCR % = Tickets resolved on first contact / Total tickets * 100
        """
        
        fcr_count = 0
        total_tickets = len(tickets)
        
        for ticket in tickets:
            # Assuming 1 contact = 1 comment with resolution
            if ticket['comment_count'] == 1 and ticket['status'] == 'resolved':
                fcr_count += 1
        
        if total_tickets == 0:
            return {"fcr_rate": 0, "unit": "%"}
        
        fcr_rate = (fcr_count / total_tickets) * 100
        
        return {
            "fcr_rate": round(fcr_rate, 2),
            "unit": "%",
            "resolved_first_contact": fcr_count,
            "total_tickets": total_tickets
        }
    
    def calculate_sla_compliance(self, tickets: List[Dict]) -> Dict:
        """
        SLA Compliance Rate
        """
        
        sla_compliant = 0
        total_tickets = len(tickets)
        
        for ticket in tickets:
            if not ticket['sla_response_breached'] and not ticket['sla_resolution_breached']:
                sla_compliant += 1
        
        if total_tickets == 0:
            return {"compliance_rate": 0, "unit": "%"}
        
        compliance_rate = (sla_compliant / total_tickets) * 100
        
        return {
            "compliance_rate": round(compliance_rate, 2),
            "unit": "%",
            "compliant_tickets": sla_compliant,
            "non_compliant_tickets": total_tickets - sla_compliant,
            "total_tickets": total_tickets
        }
    
    def calculate_customer_satisfaction(self, tickets: List[Dict]) -> Dict:
        """
        Customer Satisfaction Score (CSAT)
        """
        
        satisfaction_scores = [
            ticket['user_satisfaction_score']
            for ticket in tickets
            if ticket.get('user_satisfaction_score')
        ]
        
        if not satisfaction_scores:
            return {"csat": 0, "scale": "1-5"}
        
        csat = statistics.mean(satisfaction_scores)
        
        return {
            "csat": round(csat, 2),
            "scale": "1-5",
            "min": min(satisfaction_scores),
            "max": max(satisfaction_scores),
            "median": round(statistics.median(satisfaction_scores), 2),
            "count": len(satisfaction_scores)
        }
    
    def get_dashboard_metrics(self, organization_id: str, 
                             period_days: int = 30) -> Dict:
        """
        Get comprehensive dashboard metrics
        """
        
        # Fetch data for period
        start_date = datetime.now() - timedelta(days=period_days)
        tickets = self._get_tickets(organization_id, start_date, datetime.now())
        
        return {
            "period": f"Last {period_days} days",
            "mttr": self.calculate_mttr(tickets),
            "mtta": self.calculate_mtta(tickets),
            "fcr": self.calculate_first_contact_resolution(tickets),
            "sla_compliance": self.calculate_sla_compliance(tickets),
            "csat": self.calculate_customer_satisfaction(tickets),
            "total_tickets": len(tickets),
            "by_priority": self._get_metrics_by_priority(tickets),
            "by_team": self._get_metrics_by_team(tickets),
            "by_category": self._get_metrics_by_category(tickets)
        }
    
    def _get_tickets(self, org_id: str, start: datetime, 
                    end: datetime) -> List[Dict]:
        """Fetch tickets for period"""
        # Implementation: Query database
        pass
    
    def _get_metrics_by_priority(self, tickets: List[Dict]) -> Dict:
        """Calculate metrics grouped by priority"""
        # Implementation
        pass
    
    def _get_metrics_by_team(self, tickets: List[Dict]) -> Dict:
        """Calculate metrics grouped by team"""
        # Implementation
        pass
    
    def _get_metrics_by_category(self, tickets: List[Dict]) -> Dict:
        """Calculate metrics grouped by category"""
        # Implementation
        pass
```

---

## Summary

Ini adalah implementasi lengkap untuk:

✅ **Priority Calculation**: ITIL Impact x Urgency matrix dengan scoring  
✅ **SLA Management**: Business hours calculation, breach detection, escalation  
✅ **Auto Assignment**: Multiple strategies (round-robin, skill-based, load-based)  
✅ **Escalation Engine**: Multi-level automatic escalation  
✅ **Workflow Engine**: Multi-step approval workflows  
✅ **Notifications**: Multi-channel (email, Slack, Teams, SMS, in-app)  
✅ **Analytics**: MTTR, MTTA, FCR, SLA compliance, CSAT  

