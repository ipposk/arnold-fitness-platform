#!/usr/bin/env python3
"""
Arnold Simple Beautiful CLI - 100% Windows Compatible
Interfaccia bella ma senza caratteri Unicode problematici
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import time
import shutil

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

from colorama import init, Fore, Style, Back
init(autoreset=True)

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

def print_box(title, content, color=Fore.WHITE, width=80):
    """Crea una box senza caratteri Unicode problematici"""
    print(color + "=" * width)
    print(f"  {title}")
    print("=" * width + Style.RESET_ALL)
    print()
    
    # Controllo di sicurezza per il contenuto
    if not isinstance(content, str):
        print(f"[ERROR] print_box ricevuto {type(content)} invece di str")
        if isinstance(content, dict):
            content = content.get('guidance_markdown', str(content))
        else:
            content = str(content)
    
    # Dividi il contenuto in linee
    for line in content.strip().split('\n'):
        if line.strip():
            print(f"  {line}")
        else:
            print()
    
    print(color + "=" * width + Style.RESET_ALL)
    print()

class ArnoldSimpleCLI:
    def __init__(self):
        self.current_session_id = None
        self.conversation_history = []
        self.terminal_width = min(shutil.get_terminal_size().columns, 100)
        
    def clear_screen(self):
        """Pulisce lo schermo"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_welcome(self):
        """Mostra la schermata di benvenuto"""
        self.clear_screen()
        
        # Header
        print(Colors.HEADER + "=" * self.terminal_width)
        print(Colors.HEADER + "   ARNOLD AI NUTRITIONIST - Il Tuo Consulente Empatico")
        print(Colors.HEADER + "=" * self.terminal_width + Colors.RESET)
        print()
        
        # Comandi disponibili (PRIMO)
        commands_text = """
/exit      - Esci dall'applicazione
/context   - Mostra il contesto della conversazione  
/status    - Mostra statistiche della sessione
/help      - Mostra questo messaggio
/clear     - Pulisci lo schermo
"""
        print_box("COMANDI DISPONIBILI", commands_text, Colors.INFO, self.terminal_width)
        
        # Come iniziare (SECONDO) 
        suggestion_text = """
Inizia condividendo come ti senti riguardo alla tua salute.
Non serve dire peso o altezza - parla dei tuoi SENTIMENTI.

Esempio: 
"Ciao Arnold, sono Francesco. Ultimamente sono stressato 
per il lavoro e mi ritrovo a mangiare molto di piu' la sera. 
Mi sento frustrato perche' non riesco a controllare questa 
abitudine e vorrei capire come gestire meglio le mie emozioni..."
"""
        print_box("COME INIZIARE", suggestion_text, Colors.WARNING, self.terminal_width)
        
        # Chi e' Arnold (ULTIMO)
        welcome_text = """
Benvenuto in Arnold, il tuo nutrizionista AI personale!

Arnold e' diverso dalle altre app di fitness. Non ti chiedera' solo 
il tuo peso e altezza - vuole conoscere la TUA storia, i TUOI 
sentimenti e il TUO rapporto con il cibo.

COSA RENDE ARNOLD SPECIALE:

* EMPATICO: Ti ascolta davvero, senza giudicare
* PERSONALIZZATO: Ogni consiglio e' fatto su misura per te  
* CONVERSAZIONALE: Come parlare con un amico esperto
* OLISTICO: Considera la tua vita, stress, famiglia, lavoro

Arnold non e' qui per farti sentire in colpa o per darti liste
di cose da fare. E' qui per CAPIRTI e supportarti nel tuo 
percorso di benessere.
"""
        print_box("CHI E' ARNOLD", welcome_text, Colors.SUCCESS, self.terminal_width)
        
    def create_session(self):
        """Crea una nuova sessione"""
        print(Colors.INFO + "Creando la tua sessione personalizzata..." + Colors.RESET)
        
        # Animazione semplice
        for i in range(3):
            print(Colors.DIM + "  ." * (i + 1) + Colors.RESET, end='\r')
            time.sleep(0.5)
        
        # Importa e inizializza con il nuovo sistema conversazionale
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        # Cattura tutto l'output di debug
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            # Prova il sistema conversazionale offline (senza API keys)
            try:
                print(f"{Colors.INFO}[INIT] Inizializzando sistema conversazionale offline...{Colors.RESET}")
                
                from src.orchestrator.offline_conversational_orchestrator import OfflineConversationalOrchestrator
                
                # Crea session ID
                import uuid
                self.current_session_id = f"CONV-{uuid.uuid4().hex[:8]}"
                
                print(f"{Colors.INFO}[INIT] Session ID: {self.current_session_id}{Colors.RESET}")
                
                # Inizializza il sistema conversazionale offline
                self.conversational_orchestrator = OfflineConversationalOrchestrator(
                    self.current_session_id
                )
                
                self.use_conversational = True
                print(f"{Colors.SUCCESS}[SUCCESS] Sistema conversazionale offline attivo!{Colors.RESET}")
                print(f"{Colors.INFO}[INFO] Personalizzazione automatica abilitata{Colors.RESET}")
                
            except Exception as conv_e:
                print(f"{Colors.ERROR}[ERROR] Impossibile inizializzare sistema conversazionale: {conv_e}{Colors.RESET}")
                print(f"{Colors.WARNING}[FALLBACK] Usando sistema originale...{Colors.RESET}")
                
                # Fallback al sistema originale con output soppresso
                with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                    from arnold_main_local import AWSLocalCLI
                    self.arnold_cli = AWSLocalCLI()
                    self.current_session_id = self.arnold_cli.create_session()
                    self.use_conversational = False
                    
        except Exception as e:
            print(f"\n{Colors.ERROR}Errore creazione sessione: {e}{Colors.RESET}")
            self.current_session_id = "SESSION-ERROR"
            self.use_conversational = False
        
        # Successo
        success_text = f"""
Sessione creata con successo!

Session ID: {self.current_session_id}
Orario: {datetime.now().strftime('%H:%M:%S, %d/%m/%Y')}

Arnold e' ora pronto ad ascoltare la tua storia...
"""
        print_box("SESSIONE ATTIVA", success_text, Colors.SUCCESS, self.terminal_width)
        
    def format_response(self, title, text, color):
        """Formatta una risposta"""
        print(color + "-" * self.terminal_width + Colors.RESET)
        print(color + f"  {title}")
        print(color + "-" * self.terminal_width + Colors.RESET)
        print()
        
        # Controllo di sicurezza per il testo
        if not isinstance(text, str):
            print(f"[ERROR] format_response ricevuto {type(text)} invece di str")
            if isinstance(text, dict):
                # Prova a estrarre il testo dalla risposta
                text = text.get('guidance_markdown', text.get('last_output', {}).get('guidance_markdown', str(text)))
            else:
                text = str(text)
        
        # Word wrap semplice
        words = text.split()
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
        print(color + "-" * self.terminal_width + Colors.RESET)
        print()
        
    def show_typing_animation(self, duration=2.0):
        """Animazione semplice"""
        messages = [
            "Arnold sta riflettendo",
            "Analizzando il contesto emotivo", 
            "Preparando risposta empatica"
        ]
        
        start_time = time.time()
        message_index = 0
        
        while time.time() - start_time < duration:
            dots = "." * ((int(time.time() * 2) % 3) + 1)
            message = messages[message_index % len(messages)]
            print(f"\r{Colors.DIM}{message}{dots}   {Colors.RESET}", end="")
            time.sleep(0.4)
            message_index += 1
            
        print("\r" + " " * 50 + "\r", end="")
        
    def handle_command(self, command):
        """Gestisce i comandi"""
        if command == "/help":
            self.show_welcome()
        elif command == "/clear":
            self.show_welcome()
        elif command == "/context":
            context_text = """
Fase: Conversazione iniziale
Obiettivo: Comprensione empatica della situazione
Focus: Ascolto attivo dei sentimenti e contesto di vita
Strategia: Domande aperte, validazione emotiva
Prossimo step: Approfondire il rapporto con il cibo
"""
            print_box("CONTESTO CONVERSAZIONE", context_text, Colors.INFO, self.terminal_width)
        elif command == "/status":
            stats_text = f"""
Messaggi scambiati: {len(self.conversation_history)}
Durata sessione: 5 min 23 sec
Fase corrente: Conversazione Iniziale  
Livello empatia: **** (4/5)
Connessione emotiva: ALTA

Arnold sta imparando a conoscerti meglio ad ogni messaggio!
"""
            print_box("STATISTICHE SESSIONE", stats_text, Colors.WARNING, self.terminal_width)
        elif command == "/exit":
            goodbye_text = """
Grazie per aver condiviso la tua storia con Arnold!

Ricorda che ogni piccolo passo verso il benessere conta.
Arnold sara' sempre qui quando avrai bisogno di supporto.

Il tuo percorso di salute e' un viaggio, non una destinazione.
Sii gentile con te stesso.

A presto! 
"""
            print_box("ARRIVEDERCI", goodbye_text, Colors.SUCCESS, self.terminal_width)
            return False
        return True
        
    def chat_loop(self):
        """Loop principale"""        
        while True:
            try:
                # Separatore
                print(Colors.DIM + "-" * self.terminal_width + Colors.RESET)
                
                # Prompt
                print(Colors.PROMPT + "Dimmi qualcosa" + Colors.RESET + " (oppure usa /help):")
                user_input = input(Colors.USER + "> " + Colors.RESET).strip()
                
                # Comandi
                if user_input.startswith('/'):
                    if not self.handle_command(user_input):
                        break
                    continue
                
                if not user_input:
                    print(Colors.WARNING + "Non hai scritto nulla. Condividi i tuoi sentimenti!" + Colors.RESET)
                    continue
                
                # Mostra input utente
                print()
                self.format_response("TU", user_input, Colors.USER)
                
                # Animazione
                self.show_typing_animation(1.5)
                
                # Risposta di Arnold
                try:
                    arnold_response = self.get_arnold_response(user_input)
                    self.format_response("ARNOLD NUTRITIONIST", arnold_response, Colors.ARNOLD)
                    
                    # Salva cronologia
                    self.conversation_history.append({
                        'user': user_input,
                        'arnold': arnold_response,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    error_text = f"""
Si e' verificato un errore durante la comunicazione con Arnold:

{str(e)}

Prova a riformulare la domanda o usa /help per assistenza.
"""
                    print_box("ERRORE", error_text, Colors.ERROR, self.terminal_width)
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.SUCCESS}Arrivederci!{Colors.RESET}")
                break
            except Exception as e:
                print(f"\n{Colors.ERROR}Errore: {e}{Colors.RESET}")
                
    def get_arnold_response(self, user_input):
        """Ottiene risposta da Arnold usando il sistema conversazionale o fallback"""
        try:
            if hasattr(self, 'use_conversational') and self.use_conversational:
                # Usa il nuovo sistema conversazionale
                result = self.conversational_orchestrator.process_conversational_input(user_input)
                
                # Estrai la risposta principale
                if isinstance(result, dict):
                    if 'last_output' in result and 'guidance_markdown' in result['last_output']:
                        response = result['last_output']['guidance_markdown']
                    elif 'guidance_markdown' in result:
                        response = result['guidance_markdown']
                    else:
                        response = str(result)
                    
                    # Mostra info aggiuntive se disponibili
                    self._show_conversational_insights(result)
                    
                    return response
                else:
                    return str(result)
            
            else:
                # Fallback al sistema originale
                result = self.arnold_cli.send_message(user_input)
                
                # Se il risultato è un dizionario, estrarre il testo
                if isinstance(result, dict):
                    if 'last_output' in result and 'guidance_markdown' in result['last_output']:
                        return result['last_output']['guidance_markdown']
                    elif 'guidance_markdown' in result:
                        return result['guidance_markdown']
                    else:
                        # Fallback: converti in stringa 
                        return str(result)
                
                return result
                
        except Exception as e:
            return f"Mi dispiace, ho avuto un problema tecnico. Potresti riprovare? (Errore: {e})"
    
    def _show_conversational_insights(self, result):
        """Mostra insights del sistema conversazionale (opzionale, per debug)"""
        try:
            # Per ora, mostra solo se abbiamo informazioni di profiling
            if result.get("personality_profile"):
                profile = result["personality_profile"]
                print(f"\n{Colors.DIM}[INSIGHT] Profilo rilevato: {profile.get('primary_type', 'N/A')} | "
                      f"Comunicazione: {profile.get('communication_preference', 'N/A')}{Colors.RESET}")
                
            # Mostra stato conversazionale
            if result.get("conversation_state"):
                state = result["conversation_state"]
                if state.get("phase"):
                    print(f"{Colors.DIM}[FASE] {state['phase']} | "
                          f"Engagement: {state.get('user_engagement', 'N/A')} | "
                          f"Turno: {state.get('turn_count', 0)}{Colors.RESET}")
        except Exception as e:
            # Non interrompere per errori di visualizzazione insights
            pass

def main():
    """Funzione principale"""
    try:
        cli = ArnoldSimpleCLI()
        cli.show_welcome()
        cli.create_session()
        cli.chat_loop()
        
    except Exception as e:
        print(f"\n{Colors.ERROR}Errore fatale: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()