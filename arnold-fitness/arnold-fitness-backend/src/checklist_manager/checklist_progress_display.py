"""
Checklist Progress Display - Visualizzazione stato checklist nel CLI
"""
from typing import Dict, List, Any
from colorama import Fore, Style, Back
import json
from pathlib import Path

class ChecklistProgressDisplay:
    """
    Gestisce la visualizzazione del progresso delle checklist nel CLI
    Mostra chiaramente: completed, in_progress, pending con colori e indicatori
    """
    
    def __init__(self):
        self.colors = {
            'completed': Fore.GREEN + Style.BRIGHT,
            'in_progress': Fore.YELLOW + Style.BRIGHT,  
            'pending': Fore.WHITE + Style.DIM,
            'current': Back.BLUE + Fore.WHITE + Style.BRIGHT,
            'reset': Style.RESET_ALL
        }
    
    def display_checklist_status(self, checklist_data: Dict, current_check_id: str = None, terminal_width: int = 80) -> None:
        """
        Visualizza lo stato completo della checklist con progress bar
        """
        print(self.colors['reset'])
        print("=" * terminal_width)
        print(f"  📋 ARNOLD CHECKLIST PROGRESS - {checklist_data.get('title', 'Unknown')}")
        print("=" * terminal_width)
        print()
        
        # Progress overview
        total_checks, completed_checks, in_progress_checks = self._count_checks(checklist_data)
        progress_percentage = (completed_checks / total_checks * 100) if total_checks > 0 else 0
        
        print(f"  📊 AVANZAMENTO: {completed_checks}/{total_checks} completati ({progress_percentage:.1f}%)")
        self._draw_progress_bar(progress_percentage, terminal_width - 4)
        print()
        
        # Detailed task view
        for task in checklist_data.get('tasks', []):
            print(f"  📁 {self.colors['current']}{task['title']}{self.colors['reset']}")
            print(f"     Task ID: {task['task_id']}")
            print()
            
            # Show checks with context
            for i, check in enumerate(task.get('checks', [])):
                is_current = check['check_id'] == current_check_id
                status_icon, status_color = self._get_status_display(check['state'], is_current)
                
                print(f"    {status_color}{status_icon} {check['check_id']}{self.colors['reset']}: {check['description']}")
                
                # Show additional info for current and recent
                if is_current or check['state'] == 'completed':
                    if check.get('context_path'):
                        print(f"      💾 Context: {self.colors['pending']}{check['context_path']}{self.colors['reset']}")
                    if check.get('required_data'):
                        data_status = "✅" if check['state'] == 'completed' else "⏳"
                        print(f"      {data_status} Dati richiesti: {', '.join(check['required_data'])}")
                    if check.get('timestamp'):
                        print(f"      🕒 Completato: {check['timestamp']}")
                print()
            
        print("=" * terminal_width)
        print()
    
    def display_context_window(self, current_check: Dict, previous_check: Dict = None, next_check: Dict = None, terminal_width: int = 80) -> None:
        """
        Mostra finestra di contesto: precedente | corrente | successivo
        """
        print(self.colors['reset'])
        print("-" * terminal_width)
        print(f"  🎯 CONTESTO CHECKLIST - Focus su {current_check.get('check_id', 'N/A')}")
        print("-" * terminal_width)
        print()
        
        # Three column layout
        col_width = (terminal_width - 6) // 3
        
        # Headers
        prev_header = f"{'← PRECEDENTE':^{col_width}}"
        curr_header = f"{'● IN CORSO':^{col_width}}"
        next_header = f"{'PROSSIMO →':^{col_width}}"
        
        print(f"  {self.colors['completed']}{prev_header}{self.colors['reset']} | "
              f"{self.colors['in_progress']}{curr_header}{self.colors['reset']} | "
              f"{self.colors['pending']}{next_header}{self.colors['reset']}")
        print("  " + "-" * col_width + " | " + "-" * col_width + " | " + "-" * col_width)
        
        # Content
        prev_content = self._format_check_summary(previous_check, col_width) if previous_check else "Nessuno"
        curr_content = self._format_check_summary(current_check, col_width, highlight=True)
        next_content = self._format_check_summary(next_check, col_width) if next_check else "Fine checklist"
        
        print(f"  {prev_content} | {curr_content} | {next_content}")
        print()
        print("-" * terminal_width)
        print()
    
    def display_completion_celebration(self, completed_check: Dict, terminal_width: int = 80) -> None:
        """
        Mostra celebrazione quando un check viene completato
        """
        print()
        print(self.colors['completed'] + "🎉" * (terminal_width // 2))
        print(f"  ✅ COMPLETATO: {completed_check['check_id']}")
        print(f"     {completed_check['description']}")
        print("🎉" * (terminal_width // 2) + self.colors['reset'])
        print()
    
    def _count_checks(self, checklist_data: Dict) -> tuple:
        """Conta i check per stato"""
        total = completed = in_progress = 0
        
        for task in checklist_data.get('tasks', []):
            for check in task.get('checks', []):
                total += 1
                if check['state'] == 'completed':
                    completed += 1
                elif check['state'] == 'in_progress':
                    in_progress += 1
                    
        return total, completed, in_progress
    
    def _draw_progress_bar(self, percentage: float, width: int) -> None:
        """Disegna barra di progresso"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        print(f"  {self.colors['completed']}{bar}{self.colors['reset']} {percentage:.1f}%")
    
    def _get_status_display(self, state: str, is_current: bool = False) -> tuple:
        """Restituisce icona e colore per lo stato"""
        if is_current:
            return "👉", self.colors['current']
        elif state == 'completed':
            return "✅", self.colors['completed'] 
        elif state == 'in_progress':
            return "🔄", self.colors['in_progress']
        else:  # pending
            return "⏸️", self.colors['pending']
    
    def _format_check_summary(self, check: Dict, width: int, highlight: bool = False) -> str:
        """Formatta summary di un check per la vista a 3 colonne"""
        if not check:
            return " " * width
            
        check_id = check.get('check_id', 'N/A')
        desc = check.get('description', 'No description')
        
        # Tronca se troppo lungo
        if len(desc) > width - 10:
            desc = desc[:width-13] + "..."
            
        summary = f"{check_id}\n{desc}"
        
        if highlight:
            return f"{self.colors['in_progress']}{summary}{self.colors['reset']}"
        else:
            return summary