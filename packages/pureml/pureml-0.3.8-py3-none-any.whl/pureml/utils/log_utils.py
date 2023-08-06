
def merge_step_with_value(values_dict, step):
    value_dict_with_step = {}

    value_dict_with_step[step] = values_dict

    
    return value_dict_with_step



def update_step_dict(values_dict_existing, values_dict_new):

    for step_new in values_dict_new.keys():

        if step_new not in values_dict_existing.keys():
            values_dict_existing[step_new] = values_dict_new[step_new]
        else:
            values_dict_existing[step_new].update(values_dict_new[step_new])

    return values_dict_existing
