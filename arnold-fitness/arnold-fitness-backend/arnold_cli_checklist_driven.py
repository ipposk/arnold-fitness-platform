#!/usr/bin/env python3
"""
Arnold CLI Checklist-Driven - Implementazione della visione originale
Segue rigorosamente le checklist come binario per mantenere il contesto
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, Any

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

from colorama import init, Fore, Style, Back
init(autoreset=True)

# Import componenti checklist-driven
from src.orchestrator.checklist_driven_orchestrator import ChecklistDrivenOrchestrator
from src.checklist_manager import ChecklistProgressDisplay

class Colors:
    """Colori per la CLI"""
    HEADER = Fore.CYAN + Style.BRIGHT
    SUCCESS = Fore.GREEN + Style.BRIGHT
    WARNING = Fore.YELLOW + Style.BRIGHT
    ERROR = Fore.RED + Style.BRIGHT
    INFO = Fore.BLUE + Style.BRIGHT
    ARNOLD = Fore.GREEN + Style.BRIGHT
    USER = Fore.CYAN + Style.BRIGHT
    PROMPT = Fore.MAGENTA + Style.BRIGHT
    DIM = Style.DIM
    RESET = Style.RESET_ALL
    CHECK_COMPLETED = Fore.GREEN + Style.BRIGHT
    CHECK_IN_PROGRESS = Fore.YELLOW + Style.BRIGHT + Back.BLUE
    CHECK_PENDING = Fore.WHITE + Style.DIM

class ArnoldChecklistCLI:
    """
    Arnold CLI che implementa rigorosamente il sistema checklist-driven
    """
    
    def __init__(self):
        try:
            self.terminal_width = min(100, os.get_terminal_size().columns - 2)
        except OSError:
            # Fallback per ambienti non interattivi
            self.terminal_width = 80
        self.orchestrator = None
        self.progress_display = ChecklistProgressDisplay()
        self.session_id = None
        
        # Context simulato per demo (in produzione verrebbe da DynamoDB)
        self.user_context = {
            'sessions_count': 0,  # Simula primo utilizzo
            'days_since_last_session': 0
        }
        
    def run(self):
        """Avvia il CLI checklist-driven"""
        try:
            self.show_welcome()
            self.initialize_session()
            self.main_loop()
        except KeyboardInterrupt:
            print(f"\\n\\n{Colors.SUCCESS}Arrivederci da Arnold!{Colors.RESET}")
        except Exception as e:
            print(f"\\n{Colors.ERROR}Errore fatale: {e}{Colors.RESET}")
    
    def show_welcome(self):
        """Mostra schermata di benvenuto checklist-focused"""
        self.clear_screen()
        
        print(Colors.HEADER + "=" * self.terminal_width)
        print(f"   ARNOLD AI NUTRITIONIST - Sistema Checklist-Driven")
        print("=" * self.terminal_width + Colors.RESET)
        print()
        
        welcome_text = f"""
{Colors.INFO}🎯 APPROCCIO PROFESSIONALE GUIDATO{Colors.RESET}

Arnold segue un approccio sistematico basato su checklist professionali.
Ogni domanda ha uno scopo preciso per costruire il tuo profilo completo.

{Colors.SUCCESS}✅ COSA ASPETTARTI:{Colors.RESET}
• Domande strutturate e sequenziali
• Progress visibile per ogni step
• Assessment completo prima dei consigli
• Personalizzazione basata sul tuo stile di comunicazione

{Colors.WARNING}📋 VISUALIZZAZIONE PROGRESS:{Colors.RESET}
• ✅ = Completato
• 🔄 = In corso  
• ⏸️  = In attesa
• 👉 = Step corrente

{Colors.DIM}Arnold ti guiderà passo dopo passo attraverso l'assessment iniziale.{Colors.RESET}
        """
        
        print(welcome_text)
        print(Colors.HEADER + "=" * self.terminal_width + Colors.RESET)
        print()
    
    def initialize_session(self):
        """Inizializza la sessione checklist-driven"""
        print(f"{Colors.INFO}[INIT] Inizializzando sessione checklist-driven...{Colors.RESET}")
        
        # Genera session ID
        import uuid
        self.session_id = f"CHECKLIST-{uuid.uuid4().hex[:8]}"
        
        # Inizializza orchestrator con context
        self.orchestrator = ChecklistDrivenOrchestrator(
            session_id=self.session_id,
            user_context=self.user_context
        )
        
        print(f"{Colors.SUCCESS}[SUCCESS] Sistema checklist-driven attivo!{Colors.RESET}")
        print(f"{Colors.INFO}[INFO] Session ID: {self.session_id}{Colors.RESET}")
        print()
        
        # Mostra info sessione
        print(Colors.HEADER + "=" * self.terminal_width)
        print(f"   SESSIONE ATTIVA - Approccio Sistematico")
        print("=" * self.terminal_width + Colors.RESET)
        print()
        print(f"  Session ID: {self.session_id}")
        print(f"  Orario: {datetime.now().strftime('%H:%M:%S, %d/%m/%Y')}")
        print(f"  Modalità: Checklist-Driven Assessment")
        print()
        print(Colors.HEADER + "=" * self.terminal_width + Colors.RESET)
        print()
    
    def main_loop(self):
        """Loop principale del sistema checklist-driven"""
        print(f"{Colors.SUCCESS}🚀 Arnold è pronto per il tuo assessment professionale!{Colors.RESET}")
        print(f"{Colors.DIM}(Digita /help per i comandi disponibili){Colors.RESET}")
        print()
        
        # Prima interazione - mostra stato iniziale
        self.show_initial_checklist_state()
        
        while True:
            try:
                # Input utente
                user_input = self.get_user_input()
                
                if not user_input.strip():
                    continue
                    
                # Gestisci comandi speciali
                if user_input.startswith('/'):
                    if not self.handle_command(user_input):
                        break
                    continue
                
                # Processa input attraverso orchestrator checklist-driven
                self.process_user_message(user_input)
                
            except KeyboardInterrupt:
                print(f"\\n\\n{Colors.SUCCESS}Sessione salvata. Arrivederci!{Colors.RESET}")
                break
            except Exception as e:
                print(f"\\n{Colors.ERROR}Errore: {e}{Colors.RESET}")
    
    def show_initial_checklist_state(self):
        """Mostra lo stato iniziale della checklist"""
        # Ottieni contesto checklist dall'orchestrator
        checklist_context = self.orchestrator.get_checklist_context()
        
        if checklist_context.get('checklist'):
            # Mostra overview completa
            print(f"{Colors.INFO}📋 CHECKLIST INIZIALE CARICATA{Colors.RESET}")
            self.progress_display.display_checklist_status(
                checklist_context['checklist'], 
                terminal_width=self.terminal_width
            )
            
            # Mostra contesto attuale se c'è un check corrente
            if checklist_context.get('current_check'):
                self.progress_display.display_context_window(
                    checklist_context['current_check'],
                    checklist_context.get('previous_check'),
                    checklist_context.get('next_check'),
                    terminal_width=self.terminal_width
                )
        
        # Genera prima domanda
        print(f"{Colors.ARNOLD}💬 Arnold:{Colors.RESET}")
        print("   Ciao! Iniziamo il tuo assessment personalizzato.")
        print("   Dimmi, come ti chiami?")
        print()
    
    def process_user_message(self, user_input: str):
        """Processa messaggio utente attraverso l'orchestrator checklist-driven"""
        print(f"{Colors.DIM}[PROCESSING] Analizzando risposta e aggiornando checklist...{Colors.RESET}")
        
        # Processa attraverso orchestrator
        result = self.orchestrator.process_user_input(user_input)
        
        # Mostra aggiornamento stato se completato un check
        if result.get('status') == 'advancing' and result.get('checklist_state', {}).get('just_completed'):
            self.show_check_completion()
        
        # Mostra progress aggiornato
        self.show_updated_progress(result)
        
        # Mostra risposta di Arnold
        self.show_arnold_response(result['response'])
        
        # Mostra contesto finestra se disponibile
        checklist_context = self.orchestrator.get_checklist_context()
        if checklist_context.get('current_check'):
            self.progress_display.display_context_window(
                checklist_context['current_check'],
                checklist_context.get('previous_check'),
                checklist_context.get('next_check'),
                terminal_width=self.terminal_width
            )
    
    def show_check_completion(self):
        """Mostra celebrazione completamento check"""
        print()
        print(Colors.SUCCESS + "🎉" * (self.terminal_width // 4))
        print(f"  ✅ CHECK COMPLETATO!")
        print("🎉" * (self.terminal_width // 4) + Colors.RESET)
        time.sleep(0.5)  # Pausa per effetto visivo
    
    def show_updated_progress(self, result: Dict):
        """Mostra progress aggiornato"""
        checklist_state = result.get('checklist_state', {})
        progress = checklist_state.get('progress', 0)
        
        if progress > 0:
            print()
            print(f"{Colors.INFO}📊 PROGRESS AGGIORNATO: {progress:.1f}% completato{Colors.RESET}")
            
            # Barra di progresso semplice
            bar_width = self.terminal_width - 20
            filled = int(bar_width * progress / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            print(f"  {Colors.SUCCESS}{bar}{Colors.RESET} {progress:.1f}%")
            print()
    
    def show_arnold_response(self, response: str):
        """Mostra risposta di Arnold"""
        print(Colors.HEADER + "-" * self.terminal_width + Colors.RESET)
        print(f"{Colors.ARNOLD}💬 Arnold Nutritionist:{Colors.RESET}")
        print(Colors.HEADER + "-" * self.terminal_width + Colors.RESET)
        print()
        
        # Word wrap della risposta
        words = response.split()
        line = ""
        max_width = self.terminal_width - 4
        
        for word in words:
            if len(line + " " + word) <= max_width:
                line += (" " if line else "") + word
            else:
                if line:
                    print(f"  {line}")
                line = word
        
        if line:
            print(f"  {line}")
        
        print()
        print(Colors.HEADER + "-" * self.terminal_width + Colors.RESET)
        print()
    
    def get_user_input(self) -> str:
        """Ottieni input utente con prompt personalizzato"""
        print(Colors.DIM + "-" * self.terminal_width + Colors.RESET)
        try:
            return input(f"{Colors.PROMPT}Rispondi (o /help): {Colors.RESET}")
        except EOFError:
            return "/exit"
    
    def handle_command(self, command: str) -> bool:
        """Gestisce comandi speciali"""
        cmd = command.lower().strip()
        
        if cmd == "/help":
            self.show_help()
        elif cmd == "/progress":
            self.show_full_progress()
        elif cmd == "/context":
            self.show_context_details()
        elif cmd == "/checklist":
            self.show_full_checklist()
        elif cmd == "/clear":
            self.clear_screen()
            self.show_welcome()
        elif cmd == "/exit":
            return False
        else:
            print(f"{Colors.WARNING}Comando non riconosciuto: {command}{Colors.RESET}")
            print(f"{Colors.DIM}Usa /help per vedere i comandi disponibili{Colors.RESET}")
        
        return True
    
    def show_help(self):
        """Mostra aiuto comandi"""
        help_text = f"""
{Colors.HEADER}=== COMANDI DISPONIBILI ==={Colors.RESET}

{Colors.SUCCESS}/progress{Colors.RESET}   - Mostra progress completo checklist
{Colors.SUCCESS}/checklist{Colors.RESET}  - Visualizza intera checklist con stati  
{Colors.SUCCESS}/context{Colors.RESET}    - Mostra context JSON corrente
{Colors.SUCCESS}/clear{Colors.RESET}      - Pulisce schermo
{Colors.SUCCESS}/help{Colors.RESET}       - Mostra questo aiuto
{Colors.SUCCESS}/exit{Colors.RESET}       - Esci dalla sessione

{Colors.INFO}📋 SISTEMA CHECKLIST-DRIVEN:{Colors.RESET}
• Ogni domanda segue una checklist professionale
• I dati vengono raccolti sistematicamente  
• Il progress è sempre visibile
• La personalizzazione avviene solo nello stile comunicativo

{Colors.DIM}Continua a rispondere alle domande per completare l'assessment!{Colors.RESET}
        """
        print(help_text)
    
    def show_full_progress(self):
        """Mostra progress completo"""
        checklist_context = self.orchestrator.get_checklist_context()
        if checklist_context.get('checklist'):
            self.progress_display.display_checklist_status(
                checklist_context['checklist'],
                checklist_context.get('current_check', {}).get('check_id'),
                terminal_width=self.terminal_width
            )
    
    def show_context_details(self):
        """Mostra dettagli del context JSON"""
        print(f"{Colors.INFO}📄 CONTEXT JSON CORRENTE:{Colors.RESET}")
        print(Colors.DIM + "-" * self.terminal_width + Colors.RESET)
        print(json.dumps(self.orchestrator.context, indent=2, ensure_ascii=False))
        print(Colors.DIM + "-" * self.terminal_width + Colors.RESET)
    
    def show_full_checklist(self):
        """Mostra checklist completa"""
        checklist_context = self.orchestrator.get_checklist_context()
        if checklist_context.get('checklist'):
            print(f"{Colors.INFO}📋 CHECKLIST COMPLETA:{Colors.RESET}")
            print(f"Tipo: {checklist_context['checklist'].get('title', 'N/A')}")
            print(f"Phase ID: {checklist_context['checklist'].get('phase_id', 'N/A')}")
            print()
            
            self.progress_display.display_checklist_status(
                checklist_context['checklist'],
                checklist_context.get('current_check', {}).get('check_id'),
                terminal_width=self.terminal_width
            )
    
    def clear_screen(self):
        """Pulisce lo schermo"""
        os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Punto di ingresso principale"""
    print(f"{Colors.HEADER}Starting Arnold Checklist-Driven CLI...{Colors.RESET}")
    
    cli = ArnoldChecklistCLI()
    cli.run()


if __name__ == "__main__":
    main()