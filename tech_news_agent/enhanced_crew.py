# crew.py
import os, time, json, re
from crewai import Crew, Process
from crewai.events import BaseEventListener, TaskCompletedEvent
from tasks.research_task import research_task
from tasks.writing_task import write_task
from tasks.fact_check_task import fact_check_task
from agents.researcher import news_researcher
from agents.writer import news_writer
from agents.fact_checker import fact_checker
from tools.memory_tool import fact_save_tool
from evaluation.evaluate_agent import AgentEvaluator



# ------------------- ENHANCED MEMORY LOGGER -------------------
class OutputCaptureLogger(BaseEventListener):
    def __init__(self):
        super().__init__()
        self.setup_enhanced_memory()
        
    def setup_listeners(self, crew):
        pass
        
    def setup_enhanced_memory(self):
        import sqlite3
        os.makedirs("memory/db", exist_ok=True)
        self.enhanced_conn = sqlite3.connect("memory/db/enhanced_memory.db")
        cursor = self.enhanced_conn.cursor()
        
        # Agent outputs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                agent_role TEXT,
                task_description TEXT,
                output_content TEXT,
                content_length INTEGER
            )
        ''')
        
        # Execution logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_logs (
                agent_role TEXT PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                agent_role TEXT,
                task_description TEXT,
                details TEXT
            )
        ''')
        
        self.enhanced_conn.commit()
        print("✅ Enhanced memory database initialized")

    def on_task_completed(self, event: TaskCompletedEvent):
        try:
            print(f"\n🎯 [TASK COMPLETED] {event.task.description}")
            print(f"   Agent: {event.agent.role}")
            
            output_content = self._capture_output_content(event)
            print(f"   Output captured: {len(output_content)} characters")
            
            self._save_to_enhanced_memory(event.agent.role, event.task.description, output_content)
            
            # Fact-checker auto save
            if event.agent.role.lower() == "fact verification analyst":
                self._process_fact_checker_output(output_content)
                
        except Exception as e:
            print(f"❌ Error in task completion handler: {e}")

    def _capture_output_content(self, event):
        # Try multiple ways to capture task output reliably
        if hasattr(event.task, 'result') and event.task.result:
            result = event.task.result
            return str(getattr(result, 'output', result))
        elif hasattr(event, 'result') and event.result:
            return str(getattr(event.result, 'output', event.result))
        elif hasattr(event.task, 'output') and event.task.output:
            return str(event.task.output)
        else:
            # Last resort: find any attribute containing "output"
            for key, value in event.task.__dict__.items():
                if 'output' in key.lower() and value:
                    return f"From {key}: {str(value)}"
            return f"No output captured for: {event.task.description}"

    def _save_to_enhanced_memory(self, agent_role, task_description, content):
        try:
            cursor = self.enhanced_conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO agent_outputs (agent_role, timestamp, task_description, output_content, content_length)
                VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)
            ''', (agent_role, task_description, content, len(content)))
            self.enhanced_conn.commit()
            print(f"💾 Latest memory updated: {agent_role} -> {len(content)} chars")
        except Exception as e:
            print(f"❌ Enhanced memory save failed: {e}")

    def _process_fact_checker_output(self, output_content):
        try:
            print(f"🔍 Processing fact-checker output...")
            facts = self._extract_facts_from_output(output_content)
            print(f"   Found {len(facts)} facts")
            for statement, evidence, status in facts:
                if status.lower() == 'pass':
                    fact_save_tool.run(fact=statement, evidence=evidence)
        except Exception as e:
            print(f"❌ Fact-checker processing failed: {e}")

    def _extract_facts_from_output(self, output):
        facts = []
        try:
            if isinstance(output, str):
                # Parse JSON from markdown code blocks
                json_match = re.search(r'```json\n(.*?)\n```', output, re.DOTALL)
                if json_match:
                    output = json_match.group(1)
                try:
                    data = json.loads(output)
                    # Reasoning log
                    for item in data.get("reasoning_log", []):
                        statement = item.get("statement", "")
                        evidence = item.get("evidence", "")
                        status = item.get("status", "pass")
                        if statement:
                            facts.append((statement, evidence, status))
                    # Final answer array
                    for item in data.get("final_answer", []):
                        statement = item.get("statement", "")
                        evidence = item.get("evidence", "")
                        status = item.get("pass_fail", "pass")
                        if statement:
                            facts.append((statement, evidence, status))
                except Exception:
                    # Fallback: simple text parsing
                    for line in output.splitlines():
                        if 'fact:' in line.lower() or 'statement:' in line.lower():
                            facts.append((line, "From text", "pass"))
        except Exception as e:
            print(f"⚠️ Fact extraction error: {e}")
        return facts

    def __del__(self):
        if hasattr(self, 'enhanced_conn'):
            self.enhanced_conn.close()


# ------------------- UTILITY FUNCTIONS -------------------
def update_tasks_with_topic(topic="artificial intelligence"):
    research_task.description = research_task.description.replace("{topic}", topic)
    write_task.description = write_task.description.replace("{topic}", topic)
    print(f"✅ Updated tasks with topic: {topic}")

def view_enhanced_memory():
    import sqlite3
    conn = sqlite3.connect("memory/db/enhanced_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT agent_role, task_description, content_length FROM agent_outputs ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    print(f"\n📊 Enhanced memory contains {len(rows)} outputs")
    for agent, task, length in rows:
        print(f"   ✅ {agent}: {length} characters")
    conn.close()


# ------------------- MAIN EXECUTION -------------------
def main():
    print("🚀 Starting Enhanced Tech News Agent Crew")
    update_tasks_with_topic("artificial intelligence")
    
    # Setup enhanced output logger
    enhanced_logger = OutputCaptureLogger()
    
    # Crew WITHOUT CrewAI memory (avoid RAG crashes)
    crew = Crew(
        agents=[news_researcher, news_writer, fact_checker],
        tasks=[research_task, write_task, fact_check_task],
        process=Process.sequential,
        verbose=True,
        memory=False,
        share_crew=True,
        event_listeners=[enhanced_logger]
    )
    
    try:
        result = crew.kickoff()
        print("\n🎉 CREW EXECUTION COMPLETED")
        print(f"📄 Final Result: {result}")
        return result
    except Exception as e:
        print(f"❌ Crew execution failed: {e}")
        raise

if __name__ == "__main__":
    main()
    view_enhanced_memory()
