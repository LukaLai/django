import os
import struct
import re

def parse_po_string(s):
    """Parse une chaîne PO et gère les échappements"""
    if not s:
        return ""
    
    # Supprimer les guillemets de début et fin
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    
    # Gérer les échappements dans l'ordre correct
    s = s.replace('\\\\', '\x00')  # Remplacer temporairement pour éviter les conflits
    s = s.replace('\\n', '\n')
    s = s.replace('\\t', '\t')
    s = s.replace('\\"', '"')
    s = s.replace('\\r', '\r')
    s = s.replace('\x00', '\\')  # Restaurer les backslashes échappés
    
    return s

def compile_po_to_mo(po_file_path, mo_file_path):
    """Compile un fichier .po en fichier .mo sans utiliser gettext"""
      translations = {}
    
    # Lire le fichier .po
    try:
        with open(po_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(po_file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            with open(po_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
    
    # Parser amélioré pour extraire les msgid et msgstr
    lines = content.split('\n')
    current_msgid = []
    current_msgstr = []
    in_msgid = False
    in_msgstr = False
    
    for line in lines:
        line = line.strip()
        
        # Ignorer les commentaires et lignes vides
        if not line or line.startswith('#'):
            continue
            
        if line.startswith('msgid '):
            # Commencer un nouveau msgid
            if in_msgstr and current_msgid and current_msgstr:
                # Sauvegarder la traduction précédente
                msgid_text = ''.join(parse_po_string(s) for s in current_msgid)
                msgstr_text = ''.join(parse_po_string(s) for s in current_msgstr)
                if msgid_text and msgstr_text:
                    translations[msgid_text] = msgstr_text
            
            current_msgid = [line[6:].strip()]  # Enlever 'msgid '
            current_msgstr = []
            in_msgid = True
            in_msgstr = False
            
        elif line.startswith('msgstr '):
            current_msgstr = [line[7:].strip()]  # Enlever 'msgstr '
            in_msgid = False
            in_msgstr = True
            
        elif line.startswith('"') and line.endswith('"'):
            # Ligne de continuation
            if in_msgid:
                current_msgid.append(line)
            elif in_msgstr:
                current_msgstr.append(line)
    
    # Ne pas oublier la dernière traduction
    if current_msgid and current_msgstr:
        msgid_text = ''.join(parse_po_string(s) for s in current_msgid)
        msgstr_text = ''.join(parse_po_string(s) for s in current_msgstr)
        if msgid_text and msgstr_text:
            translations[msgid_text] = msgstr_text
    
    # Créer le fichier .mo
    keys = list(translations.keys())
    values = list(translations.values())
    
    # Préparer les données pour le format .mo
    koffsets = []
    voffsets = []
    kencoded = []
    vencoded = []
    
    for k, v in zip(keys, values):
        kencoded.append(k.encode('utf-8'))
        vencoded.append(v.encode('utf-8'))
    
    # Calculer les offsets
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart
    for k in kencoded:
        valuestart += len(k)
    
    koffsets = []
    voffsets = []
    
    # Offsets pour les clés
    offset = keystart
    for k in kencoded:
        koffsets.append((len(k), offset))
        offset += len(k)
    
    # Offsets pour les valeurs
    offset = valuestart
    for v in vencoded:
        voffsets.append((len(v), offset))
        offset += len(v)
    
    # Écrire le fichier .mo
    with open(mo_file_path, 'wb') as f:
        # Header
        f.write(struct.pack('<I', 0x950412de))  # Magic number
        f.write(struct.pack('<I', 0))           # Version
        f.write(struct.pack('<I', len(keys)))   # Nombre d'entrées
        f.write(struct.pack('<I', 7 * 4))       # Offset table des clés
        f.write(struct.pack('<I', 7 * 4 + 8 * len(keys)))  # Offset table des valeurs
        f.write(struct.pack('<I', 0))           # Hash table size
        f.write(struct.pack('<I', 0))           # Hash table offset
        
        # Table des offsets des clés
        for length, offset in koffsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Table des offsets des valeurs
        for length, offset in voffsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Les clés
        for k in kencoded:
            f.write(k)
        
        # Les valeurs
        for v in vencoded:
            f.write(v)

# Compiler les fichiers
po_files = [
    ('locale/en/LC_MESSAGES/django.po', 'locale/en/LC_MESSAGES/django.mo'),
    ('locale/fr/LC_MESSAGES/django.po', 'locale/fr/LC_MESSAGES/django.mo')
]

for po_path, mo_path in po_files:
    if os.path.exists(po_path):
        compile_po_to_mo(po_path, mo_path)
        print(f"Compilé: {po_path} -> {mo_path}")
    else:
        print(f"Fichier non trouvé: {po_path}")

print("Compilation terminée!")
