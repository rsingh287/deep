import os
import asyncio

# Note: Requires browser-use package
try:
    from browser_use import Agent
except ImportError:
    Agent = None

class D_E_E_P_BrowserAgent:
    def __init__(self, model_instance):
        self.model = model_instance

    async def execute_task(self, task_description):
        if not Agent:
            return {"status": "error", "message": "browser-use package not installed."}
        
        print(f"[Browser-Use] Spawning autonomous DOM-aware agent for task: {task_description}")
        
        # Inject personalized context into the task
        enhanced_task = (
            f"Task: {task_description}"
        )
        
        system_rules = (
            "You are the Antigravity Live Browser Pilot assisting Commander Mr. Ramadeep Singh.\n"
            "CRITICAL RULES:\n"
            "1. DIRECT SEARCH: If asked to search or find information, IMMEDIATELY navigate directly to a search engine like https://www.google.com and type the query.\n"
            "2. NO WANDERING: Do not aimlessly browse random links or websites. Find the most relevant search result, extract the answer, and STOP immediately.\n"
            "3. BE EFFICIENT: Your goal is speed and precision. Keep actions to an absolute minimum."
        )
        
        # Persistent Browser Session & Stealth Mode
        from browser_use import Browser
        from browser_use.controller.service import Controller
        
        # 1. Custom Tools Controller
        controller = Controller()
        
        @controller.action('Save text or data to a file on the Desktop')
        def save_file_to_desktop(filename: str, content: str):
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            file_path = os.path.join(desktop_path, filename)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Successfully saved to {file_path}"
            except Exception as e:
                return f"Failed to save file: {e}"

        # 2. Persistent Profile & Stealth
        user_data_dir = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "browser_profile")
        os.makedirs(user_data_dir, exist_ok=True)
        
        browser = Browser(
            user_data_dir=user_data_dir,
            disable_security=True,
            args=['--disable-blink-features=AutomationControlled'] # Stealth Mode
        )
        
        # 3. Instantiate the autonomous browser agent
        agent = Agent(
            task=enhanced_task,
            llm=self.model,
            browser=browser,
            controller=controller,
            use_vision=True,       # 4. True Vision Enabled
            use_judge=True,        # 5. Self-Correction Enabled
            extend_system_message=system_rules,
            max_actions_per_step=3,
        )
        
        try:
            result = await agent.run()
        finally:
            await browser.close()
            
        print(f"[Browser-Use] Task completed.")
        
        # Extract the final cleanly parsed answer instead of dumping the raw JSON history
        final_answer = result.final_result()
        if not final_answer:
            # Fallback to whatever was extracted or the raw string
            final_answer = "\n".join([x for x in result.extracted_content() if x]) or "Task completed, but no final answer was formulated."
            
        return {"status": "success", "result": final_answer}

def run_browser_task(model, task_description):
    agent = D_E_E_P_BrowserAgent(model)
    return asyncio.run(agent.execute_task(task_description))
