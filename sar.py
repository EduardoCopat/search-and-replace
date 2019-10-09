import os
import sys 
import re

topdir = sys.argv[1]
old_pattern = sys.argv[2].lower()
new_pattern = sys.argv[3].lower()
old_pattern_for_file_system = old_pattern.replace('/', '#')
new_pattern_for_file_system = new_pattern.replace('/', '#')
old_p_regex = re.compile(re.escape(old_pattern), re.IGNORECASE)

escaped_old_pattern = re.escape(old_pattern)

def Replace_file(name, dirpath, old_pattern, new_pattern):
    new_file_name = name.replace(old_pattern, new_pattern)
    os.Replace(os.path.join(dirpath, name), os.path.join(dirpath, new_file_name))
    return new_file_name

def replace_file_content(filepath):
    f = open(filepath, 'r', encoding='UTF8')
    filedata = f.read()
    f.close()

    if filepath.endswith('clas.xml') or filepath.endswith('intf.xml'):
      new_file_data = old_p_regex.sub(new_pattern.upper(), filedata)
    elif filepath.endswith('.abap'):
      
      # Replace class definitions, using with lookbehind.
      # e.g. (CLASS foo DEFINITION, CLASS foo IMPLEMENTATION)
      class_regex = re.compile('(?<=CLASS )'+escaped_old_pattern, re.IGNORECASE)
      # Replace class definitions, using with lookbehind.
      # e.g. (INTERFACE foo)
      interface_regex = re.compile('(?<=INTERFACE )'+escaped_old_pattern, re.IGNORECASE)

      # Replace type ref to defitions with lookbehind
      # e.g. DATA bar type ref to foo.
      type_ref_to_regex = re.compile('(?<=TYPE REF TO )'+escaped_old_pattern, re.IGNORECASE)
      # Replace static method calls (=>) with lookforward
      # e.g. foo=>qux( ).
      static_call_regex = re.compile(escaped_old_pattern+'(?=(.*?)\=\>)', re.IGNORECASE)
      # Replace CREATE OBJECT with lookbehind, wild card and another lookbehind
      # e.g. CREATE OBJECT bar type FOO.
      # This one is more complex, we need to use match groups. See use below
      create_type_regex = re.compile('(?<=CREATE OBJECT)(.*)(?<=TYPE )('+escaped_old_pattern+')', re.IGNORECASE )

      # Replace RAISE EXCEPTION TYPE with lookbehind
      raise_exception_regex = re.compile('(?<=RAISE EXCEPTION TYPE )'+escaped_old_pattern, re.IGNORECASE)

      # Gets what is inside the CATCH expression
      catch_regex = re.compile('(?<=CATCH )(.*)(?=.)', re.IGNORECASE )

      # Interface implememntation
      # e.g. METHOD foo~bar.
      method_interface = re.compile('(?<=METHOD )(.*)(?=~)', re.IGNORECASE )

      # INTERFACES: declaration
      # e.g. INTERFACES: if_a, if_b.
      interfaces_definition = re.compile('(?<=INTERFACES)(.*?)\.', flags=re.IGNORECASE|re.DOTALL)


      new_file_data = filedata

      new_file_data = re.sub(class_regex, new_pattern, new_file_data)
      new_file_data = re.sub(interface_regex, new_pattern, new_file_data)
      new_file_data = re.sub(type_ref_to_regex, new_pattern, new_file_data)
      new_file_data = re.sub(static_call_regex, new_pattern, new_file_data)
      new_file_data = re.sub(raise_exception_regex, new_pattern, new_file_data)

      new_file_data = re.sub(create_type_regex, 
          lambda match: '%s' % (match.group(1)+new_pattern)
      , new_file_data)

      new_file_data = re.sub(catch_regex, 
          lambda match: '%s' % (simple_substitution(match.group(1)))
      , new_file_data)

      new_file_data = re.sub(method_interface, 
          lambda match: '%s' % (simple_substitution(match.group(1)))
      , new_file_data)      

      new_file_data = re.sub(interfaces_definition, 
          lambda match: '%s' % (simple_substitution(match.group(1)))
      , new_file_data)     
      
    else:
      return

    f = open(filepath, 'w', encoding='UTF8')
    f.write(new_file_data)
    f.close()

def simple_substitution(phrase):
  # Substitute a pattern for a new one
  catch_content_regex = re.compile('('+escaped_old_pattern+')+', re.IGNORECASE)
  phrase = re.sub(catch_content_regex, new_pattern, phrase)
  return phrase

def process_file(name, dirpath):
    if old_pattern_for_file_system in name:
      name = Replace_file(name, dirpath, old_pattern_for_file_system, new_pattern_for_file_system)
      
    replace_file_content(os.path.join(dirpath, name))

def process_dir(dirpath):
  basename = os.path.basename(dirpath)
  if old_pattern_for_file_system in basename: #Replace current dir if necessary
    newbasename = basename.replace(old_pattern_for_file_system, new_pattern_for_file_system)
    new_dir_path = dirpath.replace(basename, newbasename)
    os.Replace(dirpath, new_dir_path)
    
for dirpath, dirnames, files in os.walk(topdir, False):
  if '.git' in dirpath:
    continue
  for name in files:
      if '.pdf' in name:
        continue
      process_file(name, dirpath)
  process_dir(dirpath)
