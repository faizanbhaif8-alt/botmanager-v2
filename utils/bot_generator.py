"""
AI-powered bot generation using OpenRouter with DeepSeek fallback
"""
import requests
import json
from typing import Dict, Any, Optional
from utils.config import Config

class BotGenerator:
    """Generates bot code using AI APIs with fallback logic"""
    
    def __init__(self):
        self.openrouter_key = Config.OPENROUTER_API_KEY
        self.deepseek_key = Config.DEEPSEEK_API_KEY
        self.primary_model = Config.PRIMARY_MODEL
        self.fallback_model = Config.FALLBACK_MODEL
    
    def generate_bot_code(self, prompt: str, bot_type: str = "chatbot") -> Dict[str, Any]:
        """
        Generate complete bot project files from natural language prompt
        
        Args:
            prompt: User's bot description
            bot_type: Type of bot to generate
            
        Returns:
            Dictionary with generated files and metadata
        """
        # Try primary API first (OpenRouter)
        try:
            return self._generate_via_openrouter(prompt, bot_type)
        except Exception as e:
            print(f"OpenRouter failed: {str(e)}")
            
            # Fallback to DeepSeek
            try:
                return self._generate_via_deepseek(prompt, bot_type)
            except Exception as e2:
                print(f"DeepSeek fallback failed: {str(e2)}")
                return self._generate_local_fallback(prompt, bot_type)
    
    def _generate_via_openrouter(self, prompt: str, bot_type: str) -> Dict[str, Any]:
        """Generate using OpenRouter API"""
        if not self.openrouter_key:
            raise Exception("OpenRouter API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = self._get_system_prompt(bot_type)
        
        payload = {
            "model": self.primary_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        response = requests.post(
            f"{Config.OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return self._parse_generated_code(content)
        else:
            raise Exception(f"OpenRouter API error: {response.status_code}")
    
    def _generate_via_deepseek(self, prompt: str, bot_type: str) -> Dict[str, Any]:
        """Fallback to DeepSeek API"""
        if not self.deepseek_key:
            raise Exception("DeepSeek API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = self._get_system_prompt(bot_type)
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        response = requests.post(
            f"{Config.DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return self._parse_generated_code(content)
        else:
            raise Exception(f"DeepSeek API error: {response.status_code}")
    
    def _generate_local_fallback(self, prompt: str, bot_type: str) -> Dict[str, Any]:
        """Generate basic template when APIs are unavailable"""
        bot_name = prompt[:30].replace(" ", "_").lower()
        
        return {
            "files": {
                f"{bot_name}/index.html": self._get_html_template(bot_name),
                f"{bot_name}/style.css": self._get_css_template(),
                f"{bot_name}/script.js": self._get_js_template(),
                f"{bot_name}/README.md": f"# {bot_name}\n\nGenerated from: {prompt}"
            },
            "metadata": {
                "generated_by": "local_fallback",
                "bot_name": bot_name,
                "prompt": prompt
            }
        }
    
    def _get_system_prompt(self, bot_type: str) -> str:
        """Get system prompt for code generation"""
        return f"""You are a senior full-stack developer. Generate a complete, production-ready {bot_type} application.
        
        Return ONLY valid JSON with this structure:
        {{
            "files": {{
                "index.html": "<html code>",
                "style.css": "<css code>",
                "script.js": "<javascript code>",
                "requirements.txt": "<python dependencies>",
                "app.py": "<flask backend if needed>",
                "README.md": "<documentation>"
            }},
            "metadata": {{
                "name": "project_name",
                "description": "brief description",
                "dependencies": ["list", "of", "packages"]
            }}
        }}
        
        Make all code production-ready, responsive, and include error handling.
        Use Tailwind CSS for styling and vanilla JavaScript.
        """
    
    def _parse_generated_code(self, content: str) -> Dict[str, Any]:
        """Parse AI-generated JSON response"""
        try:
            # Extract JSON from markdown if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            # Fallback to basic structure
            return {
                "files": {
                    "index.html": "<h1>Generated Bot</h1><p>Code parsing failed, but bot created</p>",
                    "README.md": f"Bot generated from prompt. Error: {str(e)}"
                },
                "metadata": {
                    "error": str(e),
                    "raw_content": content[:500]
                }
            }
    
    def _get_html_template(self, name: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="style.css">
</head>
<body class="bg-gradient-to-br from-purple-900 via-blue-900 to-black min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <div class="max-w-4xl mx-auto bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8">
            <h1 class="text-4xl font-bold text-white mb-4">{name}</h1>
            <p class="text-gray-200 mb-6">Your bot has been successfully generated!</p>
            <div id="app" class="space-y-4">
                <!-- Dynamic content here -->
            </div>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>"""
    
    def _get_css_template(self) -> str:
        return """/* Custom styles */
.backdrop-blur-lg {
    backdrop-filter: blur(16px);
}

/* Smooth transitions */
* {
    transition: all 0.3s ease;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
}"""
    
    def _get_js_template(self) -> str:
        return """// Main application logic
document.addEventListener('DOMContentLoaded', () => {
    console.log('Bot initialized successfully');
    
    const app = document.getElementById('app');
    if (app) {
        app.innerHTML = `
            <div class="bg-white/5 rounded-lg p-4">
                <h2 class="text-xl font-semibold text-white mb-2">Ready to deploy!</h2>
                <p class="text-gray-300">Your bot is now live and ready for deployment to GitHub.</p>
            </div>
        `;
    }
});"""