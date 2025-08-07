#!/usr/bin/env python3
"""
Arnold Clean Chat - Minimal Professional Chat Interface
Elegant, minimal CLI that focuses ONLY on the conversation between user and Arnold.
No technical noise, no debug output, just pure conversation.
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Minimal colors - only what's needed for chat
from colorama import init, Fore, Style
init(autoreset=True)

class ChatColors:
    """Minimal color scheme for clean chat"""
    USER = Fore.CYAN
    ARNOLD = Fore.GREEN
    SYSTEM = Fore.LIGHTBLACK_EX
    ERROR = Fore.RED
    RESET = Style.RESET_ALL

class ArnoldCleanChat:
    """Minimal chat interface for Arnold - like chatting with a real nutritionist"""
    
    def __init__(self):
        # Hide all technical setup
        self._setup_arnold_silently()
        self.session_id = None
        
    def _setup_arnold_silently(self):
        """Setup Arnold backend without any output"""
        try:
            # Import without showing any technical details
            import logging
            logging.getLogger().setLevel(logging.CRITICAL)  # Suppress all logs
            
            from arnold_main_local import ArnoldCLI
            self.arnold = ArnoldCLI()
            
        except Exception as e:
            print(f"{ChatColors.ERROR}Problema di connessione. Riprova più tardi.{ChatColors.RESET}")
            sys.exit(1)
    
    def start_chat(self):
        """Start the clean chat experience"""
        self._show_welcome()
        self._create_session_silently()
        self._chat_loop()
    
    def _show_welcome(self):
        """Minimal welcome screen"""
        self._clear_screen()
        print(f"{ChatColors.ARNOLD}Ciao! Sono Arnold, il tuo nutrizionista AI.{ChatColors.RESET}")
        print(f"{ChatColors.SYSTEM}Sono qui per aiutarti con il tuo benessere. Inizia raccontandomi come ti senti.{ChatColors.RESET}")
        print()
    
    def _create_session_silently(self):
        """Create session without any technical output"""
        try:
            # Create session hiding all technical details
            old_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            
            self.session_id = self.arnold.create_session()
            
            sys.stdout.close()
            sys.stdout = old_stdout
            
        except Exception:
            print(f"{ChatColors.ERROR}Problema di connessione. Riprova più tardi.{ChatColors.RESET}")
            sys.exit(1)
    
    def _chat_loop(self):
        """Clean conversation loop - just user and Arnold"""
        while True:
            try:
                # Get user input
                user_message = input(f"{ChatColors.USER}Tu: {ChatColors.RESET}").strip()
                
                # Handle commands
                if user_message.startswith('/'):
                    if not self._handle_command(user_message):
                        break
                    continue
                
                if not user_message:
                    continue
                
                # Show typing indicator
                self._show_typing()
                
                # Get Arnold's response (hide all technical stuff)
                arnold_response = self._get_clean_response(user_message)
                
                # Show Arnold's response
                print(f"{ChatColors.ARNOLD}Arnold: {ChatColors.RESET}{arnold_response}")
                print()
                
            except KeyboardInterrupt:
                self._graceful_exit()
                break
            except Exception:
                print(f"{ChatColors.ERROR}Arnold: Mi dispiace, ho avuto un problema. Puoi ripetere?{ChatColors.RESET}")
                print()
    
    def _get_clean_response(self, user_message):
        """Get Arnold's response hiding ALL technical output"""
        try:
            # Capture and hide ALL output from Arnold processing
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            captured_output = io.StringIO()
            
            with redirect_stdout(captured_output), redirect_stderr(captured_output):
                # Send message to Arnold
                response = self.arnold.send_message(user_message)
            
            # Extract only the conversational part
            return self._extract_conversation_text(response)
            
        except Exception as e:
            return "Mi dispiace, ho avuto un problema tecnico. Puoi ripetere la domanda?"
    
    def _extract_conversation_text(self, response):
        """Extract only the conversational text from Arnold's response"""
        if isinstance(response, dict):
            # Extract from guidance_markdown if it's a dict
            if 'last_output' in response and 'guidance_markdown' in response['last_output']:
                text = response['last_output']['guidance_markdown']
            elif 'guidance_markdown' in response:
                text = response['guidance_markdown']
            else:
                text = str(response)
        else:
            text = str(response)
        
        # Clean up the text - remove all technical formatting
        clean_text = self._clean_arnold_text(text)
        return clean_text
    
    def _clean_arnold_text(self, text):
        """Clean Arnold's text from technical formatting"""
        import re
        
        # Remove markdown headers
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # Remove troubleshooting sections
        text = re.sub(r'## Assistenza Troubleshooting.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL)
        
        # Remove problem original sections
        text = re.sub(r'\*\*Problema originale:\*\*.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL)
        
        # Remove command references
        text = re.sub(r'\*\*Comando correlato:\*\*.*?(?=\n|\Z)', '', text, flags=re.MULTILINE)
        
        # Remove markdown bold/italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # If text is still too technical or empty, provide fallback
        if not text or len(text) < 10:
            return "Dimmi di più su come ti senti riguardo alla tua alimentazione."
        
        return text
    
    def _show_typing(self):
        """Simple typing indicator"""
        print(f"{ChatColors.SYSTEM}Arnold sta scrivendo...{ChatColors.RESET}", end="", flush=True)
        time.sleep(0.8)  # Brief pause for realism
        print("\r" + " " * 30 + "\r", end="")  # Clear the typing indicator
    
    def _handle_command(self, command):
        """Handle chat commands (hidden from normal flow)"""
        cmd = command.lower().strip()
        
        if cmd == '/exit':
            self._graceful_exit()
            return False
        
        elif cmd == '/help':
            self._show_help()
        
        elif cmd == '/context':
            self._show_context()
        
        elif cmd == '/status':
            self._show_status()
        
        elif cmd == '/clear':
            self._clear_screen()
            print(f"{ChatColors.ARNOLD}Arnold: Ripartiamo da capo. Come ti senti oggi?{ChatColors.RESET}")
            print()
        
        else:
            print(f"{ChatColors.SYSTEM}Comando non riconosciuto. Usa /help per vedere i comandi disponibili.{ChatColors.RESET}")
            print()
        
        return True
    
    def _show_help(self):
        """Show available commands"""
        print(f"{ChatColors.SYSTEM}Comandi disponibili:")
        print(f"  /help    - Mostra questo aiuto")
        print(f"  /context - Mostra lo stato della conversazione") 
        print(f"  /status  - Mostra statistiche della sessione")
        print(f"  /clear   - Pulisci schermo")
        print(f"  /exit    - Termina la conversazione{ChatColors.RESET}")
        print()
    
    def _show_context(self):
        """Show conversation context (for power users)"""
        try:
            # Get context from Arnold silently
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            captured = io.StringIO()
            with redirect_stdout(captured), redirect_stderr(captured):
                context = self.arnold.get_current_context()
            
            # Show only relevant information
            print(f"{ChatColors.SYSTEM}Stato della conversazione:")
            if context and 'current_phase_id' in context:
                phase = context.get('current_phase_id', 'Unknown')
                print(f"  Fase attuale: {phase}")
            
            if context and 'goal' in context:
                goal = context.get('goal', 'Non definito')
                print(f"  Obiettivo: {goal}")
            
            print(f"{ChatColors.RESET}")
            
        except Exception:
            print(f"{ChatColors.SYSTEM}Informazioni di contesto non disponibili al momento.{ChatColors.RESET}")
        print()
    
    def _show_status(self):
        """Show session status (for power users)"""
        print(f"{ChatColors.SYSTEM}Sessione attiva")
        if self.session_id:
            print(f"  ID: {self.session_id}")
        print(f"  Orario: {datetime.now().strftime('%H:%M, %d/%m/%Y')}{ChatColors.RESET}")
        print()
    
    def _clear_screen(self):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _graceful_exit(self):
        """Clean exit"""
        print(f"\n{ChatColors.ARNOLD}Arnold: È stato un piacere aiutarti! Prenditi cura di te.{ChatColors.RESET}")
        print(f"{ChatColors.SYSTEM}Arrivederci!{ChatColors.RESET}")

def main():
    """Start the clean chat experience"""
    try:
        chat = ArnoldCleanChat()
        chat.start_chat()
    except KeyboardInterrupt:
        print(f"\n{ChatColors.SYSTEM}Arrivederci!{ChatColors.RESET}")
    except Exception as e:
        print(f"{ChatColors.ERROR}Problema inaspettato. Riavvia l'applicazione.{ChatColors.RESET}")

if __name__ == "__main__":
    main()