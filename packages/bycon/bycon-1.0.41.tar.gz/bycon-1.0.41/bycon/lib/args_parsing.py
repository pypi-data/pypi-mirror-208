import argparse, os, re, yaml
from humps import decamelize

################################################################################

def get_bycon_args(byc):

	if byc.get("check_args", False) is False:
		return byc

	# Serves as "we've been here before" marker - before the env check.
	byc.update({"check_args": False})

	if not "local" in byc["env"]:
		return byc

	if byc["script_args"]:
		a_k_s = list(byc["argument_definitions"].keys())
		for a_d_k in a_k_s:
			if a_d_k not in byc["script_args"]:
				byc["argument_definitions"].pop(a_d_k, None)
	
	create_args_parser(byc)

	return byc

################################################################################

def create_args_parser(byc):

	if not "local" in byc["env"]:
		return byc

	parser = argparse.ArgumentParser()
	for d_k, defs in byc["argument_definitions"].items():
		parser.add_argument(*defs.pop("flags"), **defs)
	byc.update({ "args": parser.parse_args() })

	return byc

################################################################################

def args_update_form(byc):

	if not "local" in byc["env"]:
		return byc

	arg_vars = vars(byc["args"])

	for p in arg_vars.keys():
		if arg_vars[p] is None:
			continue
		p_d = decamelize(p)
		if p in byc["config"]["form_list_pars"]["items"]:
			byc["form_data"].update({p_d: arg_vars[p].split(',') })
		else:
			byc["form_data"].update({p_d: arg_vars[p]})

	return byc

################################################################################

def genome_binning_from_args(byc):

    if byc["args"].key:
        byc.update({"genome_binning": byc["args"].key})

    return byc

################################################################################

def filters_from_args(byc):

    if not "args" in byc:
        return

    if not "filters" in byc:
        byc.update({"filters":[]})

    if byc["args"].filters:
        for f in re.split(",", byc["args"].filters):
            byc["filters"].append({"id":f})
 
    return byc

################################################################################

def set_collation_types(byc):

    if byc["args"].collationtypes:
        s_p = {}
        for p in re.split(",", byc["args"].collationtypes):
            if p in byc["filter_definitions"].keys():
                s_p.update({p:byc["filter_definitions"][p]})
        if len(s_p.keys()) < 1:
            print("No existing collation type was provided with -c ...")
            exit()

        byc.update({"filter_definitions":s_p})

    return byc

################################################################################

def set_processing_modes(byc):

    byc.update({"update_mode": False})

    try:
        if byc["test_mode"] is True:
            byc.update({"update_mode": False})
            print( "¡¡¡ TEST MODE - no db update !!!")
            return byc
    except:
        pass

    try:
        if byc["args"].update:
            byc.update({"update_mode": True})
            print( "¡¡¡ UPDATE MODE - may overwrite entries !!!")
    except:
        pass
        
    return byc
