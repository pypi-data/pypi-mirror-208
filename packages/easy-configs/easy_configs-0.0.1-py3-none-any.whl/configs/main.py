def get_from_raw_text(name, text):
        content = text.splitlines()
        for i in range(len(content)):
            content[i] = content[i].replace('\n', '')

        target_content = ""
        target_line = ""

        for line in content:
            if f'<{name}>' in line:
                if (target_line == line):
                    target_content+=f" : {str(line).split(f'<{name}>')[1].split(f'</{name}>')[0]}"
                else:
                    target_content = str(line).split(f'<{name}>')[1].split(f'</{name}>')[0]
                    target_line = line
        
        return target_content

def get(filename, name):
        f = open(filename, 'r')
        file = f
        content = file.readlines()

        for i in range(len(content)):
            content[i] = content[i].replace('\n', '')

        target_content = ""
        target_line = ""

        for line in content:
            if f'<{name}>' in line:
                if (target_line == line):
                    target_content+=f" : {str(line).split(f'<{name}>')[1].split(f'</{name}>')[0]}"
                else:
                    target_content = str(line).split(f'<{name}>')[1].split(f'</{name}>')[0]
                    target_line = line
    
        return target_content

class Reader:
    def __init__(self):
        self.v = 1.0

    def get(filename, name):
        f = open(filename, 'r')
        file = f
        content = file.readlines()

        for i in range(len(content)):
            content[i] = content[i].replace('\n', '')

        target_content = ""
        target_line = ""

        for line in content:
            if f'<{name}>' in line:
                if (target_line == line):
                    target_content+=f" : {str(line).split(f'<{name}>')[1].split(f'</{name}>')[0]}"
                else:
                    target_content = str(line).split(f'<{name}>')[1].split(f'</{name}>')[0]
                    target_line = line
    
        return target_content
    
    def get_from_raw_text(name, text):
        content = text.splitlines()
        for i in range(len(content)):
            content[i] = content[i].replace('\n', '')

        target_content = ""
        target_line = ""

        for line in content:
            if f'<{name}>' in line:
                if (target_line == line):
                    target_content+=f" : {str(line).split(f'<{name}>')[1].split(f'</{name}>')[0]}"
                else:
                    target_content = str(line).split(f'<{name}>')[1].split(f'</{name}>')[0]
                    target_line = line
        
        return target_content
    def loads(text):
        content = text.splitlines()
        for i in range(len(content)):
            content[i] = content[i].replace('\n', '')


        array = {}
        for line in content:
            if (line == '' or line == ' ' or line == '  ' or line == '   ' or line == '    '):
                continue
            try:
                name = line.split('</')[1].replace('\n', '')
                try:
                    name = name.replace('>', '')
                except:
                    pass
                try:
                    name = name.replace('<', '')
                except:
                    pass
                array[name] = get_from_raw_text(name, text)
            except Exception as e:
                try:
                    if (line == '' or line == ' ' or line == '  ' or line == '   ' or line == '    '):
                        continue
                    name = line.split('</')[0]
                    try:
                        name = name.replace('>', '')
                    except:
                        pass
                    try:
                        name = name.replace('<', '')
                    except:
                        pass
                    array[name] = get_from_raw_text(name, text)
                except Exception as err:
                    print(err)
        return array
    def load(f):
        f = open(f.name, 'r')
        file = f
        content = file.readlines()
        for i in range(len(content)):
            content[i] = content[i].replace('\n', '')


        array = {}
        for line in content:
            if (line == '' or line == ' ' or line == '  ' or line == '   ' or line == '    '):
                continue
            try:
                name = line.split('</')[1].replace('\n', '')
                try:
                    name = name.replace('>', '')
                except:
                    pass
                try:
                    name = name.replace('<', '')
                except:
                    pass
                array[name] = get(f.name, name)
            except Exception as e:
                try:
                    if (line == '' or line == ' ' or line == '  ' or line == '   ' or line == '    '):
                        continue
                    name = line.split('</')[0]
                    try:
                        name = name.replace('>', '')
                    except:
                        pass
                    try:
                        name = name.replace('<', '')
                    except:
                        pass
                    array[name] = get(f.name, name)
                except Exception as err:
                    raise(err)
        return array


class Dumper:
    def __init__(self):
        self.v = 1.0
    
    def add(filename, name, value):
        f = open(filename, 'a')
        f.write(f'<{name}>{value}</{name}>\n')
        return f'<{name}>{value}</{name}>\n'

    def dump(filename, names: list, values: list):
        if (len(values) == len(names)):
            pass
        else:
            raise(Exception('Names List needs to be as long as the values list!'))
        f = open(filename, 'a')
        written = []
        for i, name in enumerate(names):
            f.write(f'<{name}>{values[i]}</{name}>\n')
            written.append(f'<{name}>{values[i]}</{name}>\n')
        
        return written

    def create_basic(filename):
        f = open(filename, 'w')
        f.write('<Version>1.0</Version>')
        return '<Version>1.0</Version>'

if __name__ == '__main__':
    file = open('config.config', 'w+') # open config file.
    config = Reader.load(f=file) # one way is the load function it uses an file object and then reads the config from there.
    print(config)
    # or:
    # text = file.read()
    #  config = Reader.loads(text) # Loads the config from text.
    # Get a spicific value from config without loading it: Reader.get(filename='config.config', name='The Name') # returns the value of the given name from the config.
    # Get a spicific value from config text: Reader.get_from_raw_text(name='The Name', text='Text to find the name in') # returns the value of the given name from the text
    Dumper.create_basic(filename='config.config') # creates a basic config and writes Version 1.0 in it.
    # Write something to the config: Dumper.add(filename='config.config', name='The Name', value='The Value')
    # Write Moultiple Things to your config: Dumper.dump(filename='config.config', names=['System'], values=['Windows']) # it uses the enmurate function.