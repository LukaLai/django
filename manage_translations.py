#!/usr/bin/env python3
"""
Gestionnaire de traductions Django sans gettext
Permet d'ajouter, modifier et compiler les traductions
"""

import os
import re
from datetime import datetime

def extract_translatable_strings(file_path):
    """Extrait les chaînes traduisibles d'un fichier template ou Python"""
    strings = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
    
    # Patterns pour détecter les chaînes traduisibles
    patterns = [
        r'{% trans ["\']([^"\']+)["\'] %}',  # Template Django
        r'{% trans ["\']([^"\']+)["\']',      # Template Django sans %}
        r'_\(["\']([^"\']+)["\']\)',          # Python gettext
        r'gettext\(["\']([^"\']+)["\']\)',    # Python gettext long
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        strings.update(matches)
    
    return strings

def scan_project_for_strings(base_dir):
    """Scan tout le projet pour trouver les chaînes traduisibles"""
    all_strings = set()
    
    for root, dirs, files in os.walk(base_dir):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if file.endswith(('.py', '.html')):
                file_path = os.path.join(root, file)
                strings = extract_translatable_strings(file_path)
                all_strings.update(strings)
    
    return all_strings

def read_po_file(po_path):
    """Lit un fichier .po et retourne un dictionnaire des traductions"""
    translations = {}
      if not os.path.exists(po_path):
        return translations
    
    try:
        with open(po_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(po_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            with open(po_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
    
    lines = content.split('\n')
    current_msgid = []
    current_msgstr = []
    in_msgid = False
    in_msgstr = False
    
    for line in lines:
        line = line.strip()
        
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('msgid '):
            if in_msgstr and current_msgid and current_msgstr:
                msgid_text = ''.join(s[1:-1] for s in current_msgid if s.startswith('"') and s.endswith('"'))
                msgstr_text = ''.join(s[1:-1] for s in current_msgstr if s.startswith('"') and s.endswith('"'))
                if msgid_text:
                    translations[msgid_text] = msgstr_text
            
            current_msgid = [line[6:].strip()]
            current_msgstr = []
            in_msgid = True
            in_msgstr = False
            
        elif line.startswith('msgstr '):
            current_msgstr = [line[7:].strip()]
            in_msgid = False
            in_msgstr = True
            
        elif line.startswith('"') and line.endswith('"'):
            if in_msgid:
                current_msgid.append(line)
            elif in_msgstr:
                current_msgstr.append(line)
    
    # Dernière traduction
    if current_msgid and current_msgstr:
        msgid_text = ''.join(s[1:-1] for s in current_msgid if s.startswith('"') and s.endswith('"'))
        msgstr_text = ''.join(s[1:-1] for s in current_msgstr if s.startswith('"') and s.endswith('"'))
        if msgid_text:
            translations[msgid_text] = msgstr_text
    
    return translations

def write_po_file(po_path, translations, language_name):
    """Écrit un fichier .po avec les traductions"""
    
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(po_path), exist_ok=True)
    
    with open(po_path, 'w', encoding='utf-8') as f:
        # Header du fichier PO
        f.write('# Traductions pour {}\n'.format(language_name))
        f.write('# Copyright (C) {}\n'.format(datetime.now().year))
        f.write('#\n')
        f.write('msgid ""\n')
        f.write('msgstr ""\n')
        f.write('"Project-Id-Version: Mon Blog Django\\n"\n')
        f.write('"Report-Msgid-Bugs-To: \\n"\n')
        f.write('"POT-Creation-Date: {}\\n"\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M%z')))
        f.write('"PO-Revision-Date: {}\\n"\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M%z')))
        f.write('"Language: {}\\n"\n'.format(language_name))
        f.write('"MIME-Version: 1.0\\n"\n')
        f.write('"Content-Type: text/plain; charset=UTF-8\\n"\n')
        f.write('"Content-Transfer-Encoding: 8bit\\n"\n')
        f.write('\n')
        
        # Trier les traductions par ordre alphabétique
        for msgid in sorted(translations.keys()):
            msgstr = translations[msgid]
            f.write('msgid "{}"\n'.format(msgid.replace('"', '\\"')))
            f.write('msgstr "{}"\n'.format(msgstr.replace('"', '\\"')))
            f.write('\n')

def update_translations():
    """Met à jour les fichiers de traduction"""
    
    print("🔍 Recherche des chaînes traduisibles...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    found_strings = scan_project_for_strings(base_dir)
    
    print(f"✅ {len(found_strings)} chaînes trouvées")
    
    # Langues supportées
    languages = {
        'fr': 'Français',
        'en': 'English'
    }
    
    for lang_code, lang_name in languages.items():
        print(f"\n📝 Mise à jour de {lang_name} ({lang_code})...")
        
        po_path = os.path.join(base_dir, 'locale', lang_code, 'LC_MESSAGES', 'django.po')
        
        # Lire les traductions existantes
        existing_translations = read_po_file(po_path)
        
        # Ajouter les nouvelles chaînes
        updated_translations = existing_translations.copy()
        new_strings = 0
        
        for string in found_strings:
            if string not in updated_translations:
                # Pour le français, laisser vide pour traduction manuelle
                # Pour l'anglais, utiliser la chaîne originale
                updated_translations[string] = string if lang_code == 'en' else ''
                new_strings += 1
        
        # Écrire le fichier mis à jour
        write_po_file(po_path, updated_translations, lang_code)
        
        print(f"   📁 {po_path}")
        print(f"   ➕ {new_strings} nouvelles chaînes ajoutées")
        print(f"   📊 {len(updated_translations)} traductions au total")

def add_translation(msgid, msgstr_fr, msgstr_en=None):
    """Ajoute manuellement une traduction"""
    
    if msgstr_en is None:
        msgstr_en = msgid
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Français
    po_path_fr = os.path.join(base_dir, 'locale', 'fr', 'LC_MESSAGES', 'django.po')
    translations_fr = read_po_file(po_path_fr)
    translations_fr[msgid] = msgstr_fr
    write_po_file(po_path_fr, translations_fr, 'fr')
    
    # Anglais
    po_path_en = os.path.join(base_dir, 'locale', 'en', 'LC_MESSAGES', 'django.po')
    translations_en = read_po_file(po_path_en)
    translations_en[msgid] = msgstr_en
    write_po_file(po_path_en, translations_en, 'en')
    
    print(f"✅ Traduction ajoutée: '{msgid}' -> FR: '{msgstr_fr}', EN: '{msgstr_en}'")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'update':
            update_translations()
        elif command == 'add' and len(sys.argv) >= 4:
            msgid = sys.argv[2]
            msgstr_fr = sys.argv[3]
            msgstr_en = sys.argv[4] if len(sys.argv) > 4 else msgid
            add_translation(msgid, msgstr_fr, msgstr_en)
        else:
            print("Usage:")
            print("  python manage_translations.py update")
            print("  python manage_translations.py add 'msgid' 'traduction_fr' ['traduction_en']")
    else:
        print("🌍 Gestionnaire de traductions Django")
        print("\nCommandes disponibles:")
        print("  update - Met à jour les fichiers de traduction")
        print("  add    - Ajoute une traduction manuelle")
        print("\nExemples:")
        print("  python manage_translations.py update")
        print("  python manage_translations.py add 'Hello' 'Bonjour'")
