

def add_test_result(program, test_name, test_object, unique_key=None, unique_value=None):
    if program.has_key('tests'):
        if program['tests'].has_key(test_name):
            if not unique_key or not unique_value:
                program['tests'][test_name].append(test_object)
            else:
                for t in program['tests'][test_name]:
                    if t.has_key(unique_key) and t[unique_key] == unique_value:
                        program['tests'][test_name].remove(t)
                        program['tests'][test_name].append(test_object)
                        return program
                
                program['tests'][test_name].append(test_object)
        else:
            program['tests'][test_name] = [test_object]
    else:
        program["tests"] = { test_name: [test_object] }

    return program
