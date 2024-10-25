"""
Contains everything necessary for looking up Latin words and their definitions.
Uses the PyWORDS library: https://github.com/sjgallagher2/PyWORDS

Much of this code is copied from the PyWORDS library with some modifications for easier use.
TODO: make a PyWORDS fork with this stuff in it.
"""

import pywords.lookup as lookup
from pywords.matchfilter import MatchFilter
import pywords.utils as pwutils
import re
import pywords.definitions as definitions
import os

def _get_verb_dictionary(m: lookup.WordMatch,markdown_fmt=False):
    # ex. singular indicative present active 1st person
    #V     1 1 PRES  ACTIVE  IND  1 S  1 1 o             X A
    # ex. infinitive
    #V     1 1 PRES  ACTIVE  INF  0 X  2 3 are           X A

    # TODO Fix semi-deponent, defective, and impersonal verbs

    entry = m.dl_entry
    dictstr = ''
    dict_result = {}

    if entry.verb_kind == 'DEP':
        vinfl = definitions.VerbInfl(conj=entry.conj,tense='PRES',voice='PASSIVE')
    elif entry.verb_kind == 'SEMIDEP':
        vinfl = definitions.VerbInfl(conj=entry.conj,tense='PRES',voice='ACTIVE')
    else:
        vinfl = definitions.VerbInfl(conj=entry.conj,tense='PRES',voice='ACTIVE')

    if entry.verb_kind == 'IMPERS':
        infl_filt = MatchFilter(ages=['X'],frequencies=['X','A'],variants=[entry.variant,'0'],
                persons=['0','3'],moods=['IND','INF'])
    else:
        infl_filt = MatchFilter(ages=['X'],frequencies=['X','A'],variants=[entry.variant,'0'],
                persons=['0','1'],moods=['IND','INF'])
    matches = [v for v in definitions.inflections[entry.pos] if vinfl.matches(v)]
    matches = [ma for ma in matches if infl_filt.check_inflection(ma,'V')]
    end1='' # sg ind pres active 1st person
    stem1=''
    end2='' # pres active infinitive
    stem2=''
    for ma in matches:
        if entry.verb_kind == 'IMPERS':
            if ma.person == '3' and ma.mood == 'IND' and not end1:
                end1 = ma.ending_uvij
                stem1=ma.stem
            elif ma.mood == 'INF' and not end2:
                end2 = ma.ending_uvij
                stem2 = ma.stem
        else:
            if ma.person == '1' and ma.mood == 'IND' and not end1:
                end1 = ma.ending_uvij
                stem1=ma.stem
            elif ma.mood == 'INF' and not end2:
                end2 = ma.ending_uvij
                stem2 = ma.stem

    if stem1 and stem2:
        stems = []
        if markdown_fmt:
            dictstr += '**'
        stems.append(m.get_stem(stem1)+end1)
        dictstr += m.get_stem(stem1)+end1
        dictstr += ', '
        stems.append(m.get_stem(stem2)+end2)
        dictstr += m.get_stem(stem2)+end2
        if m.dl_stem3 != '-':
            dictstr += ', '
            if entry.verb_kind == 'IMPERS':
                stems.append(m.dl_stem3+'it')
                dictstr += m.dl_stem3+'it'
            else:
                stems.append(m.dl_stem3+'i')
                dictstr += m.dl_stem3+'i'
        if m.dl_stem4 != '-':
            dictstr += ', '
            stem4str = ""
            if entry.verb_kind == 'IMPERS':
                stem4str += m.dl_stem4+'um est'
                dictstr += m.dl_stem4+'um est'
            else:
                stem4str += m.dl_stem4+'us'
                dictstr += m.dl_stem4+'us'
            if entry.verb_kind in ['DEP','SEMIDEP']:
                stem4str += ' sum'
                dictstr += ' sum'
            stems.append(stem4str)
        if markdown_fmt:
            dictstr += '**'
        dictstr += ' '
        
        dict_result["principal_parts"] = stems
    else:
        if markdown_fmt:
            dictstr += '**'
        dictstr += m.match_stem+m.match_ending
        if markdown_fmt:
            dictstr += '**'
        dictstr += ' '

    if entry.conj in ['1','2']:
        dict_result["conjugation"] = entry.conj
        dictstr += '['+entry.conj+'] '
    elif entry.conj in ['3','8']:
        if entry.variant in ['0','1']:
            dict_result["conjugation"] = 3
            dictstr += '[3] '
        elif entry.variant in ['2','3']:
            dict_result["conjugation"] = "irreg"
            dictstr += '[irreg] '
        elif entry.variant == '4':
            dict_result["conjugation"] = 4
            dictstr += '[4] '
    elif entry.conj == '7':
        if entry.variant in ['1','3']:
            dict_result["conjugation"] = 3
            dictstr += '[3] '
        else:
            dict_result["conjugation"] = "irreg"
            dictstr += '[irreg] '
    elif entry.conj in ['5','6']:
        dict_result["conjugation"] = "irreg"
        dictstr += '[irreg] ' # Irregular
    # else      Abbreviations, indeclinable, etc can be skipped
    
    if entry.verb_kind == 'TRANS':
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "transitive"
        dictstr += 'vt'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '
    elif entry.verb_kind == 'INTRANS':
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "intransitive"
        dictstr += 'vi'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '
    elif entry.verb_kind == 'SEMIDEP':
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "semideponent"
        dictstr += 'v semidep'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '
    elif entry.verb_kind == 'DEP':
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "deponent"
        dictstr += 'v dep'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '
    elif entry.verb_kind == 'IMPERS':
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "impersonal"
        dictstr += 'impers v'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '
    elif entry.verb_kind == 'PERFDEF':
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "perfect definite"
        dictstr += 'perf def v'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '
    elif entry.verb_kind == 'GEN':
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "takes genitive"
        dictstr += '(w/ gen)'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '
    elif entry.verb_kind == 'DAT':
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "takes dative"
        dictstr += '(w/ dat)'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '
    elif entry.verb_kind == 'ABL':
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "takes ablative"
        dictstr += '(w/ abl)'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '
    else:
        if markdown_fmt:
            dictstr += '*'
        dict_result["kind"] = "transitive"
        dictstr += 'vt'
        if markdown_fmt:
            dictstr += '*'
        dictstr += ' '

    dict_result["senses"] = entry.senses

    return dict_result


def _get_noun_dictionary(m: lookup.WordMatch,full_info=False,header_only=False,markdown_fmt=False):
    """
    Generate a dictionary string for a noun
    Includes:
        - principle parts
        - gender
        - kinds and modifiers (singular only, plural only)
        - senses
        - meta data (age, area, geography, frequency, and source)
    """
    # 1. Start with principle parts, same for all variants except undeclined
    princ_parts = ['','']

    if not isinstance(m.dl_entry,definitions.DictlineNounEntry):
        raise ValueError("Match passed to _get_noun_dictionary_string() is not a DictlineNounEntry match.")
    if m.dl_entry.decl == '9':
        princ_parts[0] += m.match_stem
    else:
        # Get nom. and gen. singular stem
        infls = definitions.get_possible_inflections(m.dl_entry,infl_ages=['X'],infl_frequencies=['A'])
        nom_infl = [infl for infl in infls if infl.case=='NOM' and infl.number=='S'][0]
        nom_stem = m.get_stem(nom_infl.stem)
        nom_stem = '' if nom_stem == '-' else nom_stem
        gen_infl = [infl for infl in infls if infl.case=='GEN' and infl.number=='S'][0]
        gen_stem = m.get_stem(gen_infl.stem)
        gen_stem = '' if gen_stem == '-' else gen_stem

        princ_parts[0] = nom_stem + nom_infl.ending_uvij if nom_stem else ''
        princ_parts[1] = gen_stem + gen_infl.ending_uvij if gen_stem else ''

    # 2. Get gender
    # You can use genders or genders_short here
    # gender = definitions.genders[m.dl_entry.gender]  # e.g. 'masc.', 'fem.'
    gender = definitions.genders_short[m.dl_entry.gender]  # e.g. 'm', 'f'

    # 3. Get kind or modifier
    # These include noun_kind='S','M' (singular only, multiple only)
    kind = ''
    variant = ''
    if m.dl_entry.noun_kind == 'S':  # Included here, but not actually used in DICTLINE
        kind = 'sing.'
    elif m.dl_entry.noun_kind == 'M':
        kind = 'pl.'
    # Check if this variant has a string associated with it (e.g. 'Greek')
    varstr = definitions.noun_variants[m.dl_entry.decl][m.dl_entry.variant]
    if varstr != '':
        variant = varstr

    # 4. frequency, age, geography, subject area, source
    frequency = m.dl_entry.get_frequency()
    if m.dl_entry.age != 'X':
        age = m.dl_entry.get_age()
    else:
        age = ''
    if m.dl_entry.geog != 'X':
        geography = m.dl_entry.get_geography()
    else:
        geography = ''
    subject_area = m.dl_entry.get_area()
    #source = m.dl_entry.get_source()
    source = m.dl_entry.get_source_short()  # Abbreviations like 'OLD' and 'L+S', or just author's name

    # 5. senses
    senses = m.dl_entry.senses

    # *************************
    # Put it all together
    # Note: each dictionary element adds a space after itself to prepare for the next element.
    outstr = ''
    outdict = {}
    if princ_parts[0] and princ_parts[1]:
        outdict['principal_parts'] = [princ_parts[0], princ_parts[1]]
        outstr += '**'+princ_parts[0]+'**, **'+princ_parts[1]+'** ' if markdown_fmt else princ_parts[0]+', '+princ_parts[1]+' '
    elif princ_parts[0]:  # Indeclinable usually
        outdict["principal_parts"] = [princ_parts[0]]
        outstr += '**'+princ_parts[0]+'** ' if markdown_fmt else princ_parts[0]+' '
    elif princ_parts[1]:  # Indeclinable sometimes only has second stem
        outdict["principal_parts"] = [princ_parts[1]]
        outstr += '**'+princ_parts[1]+'** ' if markdown_fmt else princ_parts[1]+' '

    else:
        raise ValueError("Error when printing noun. No principle parts were found, or only second principle part. Entry: {0}".format(m.dl_entry))
    if header_only:
        return outstr[:-1]  # Return output, leave out extra space

    outdict["gender"] = gender
    outstr += '*'+gender if markdown_fmt else gender+' '
    if kind:
        outdict["kind"] = kind
        outstr += ' '+kind+'* ' if markdown_fmt else kind+' '
    else:
        outstr += '* ' if markdown_fmt else ''

    # Variant (e.g. 'Greek'), and meta data (e.g. 'Medieval', 'most common')
    if variant or (full_info and (age or geography or frequency or subject_area)):
        # Add relevant geography, age, frequency, and subject area
        outstr += '('
        first = True  # Whether we've included some info already
        if variant:
            outstr += variant
            first = False
        if full_info:
            if frequency:
                outstr += frequency if first else ', '+frequency
                first = False  # This is the first one, next one (if any) needs to add ', '
            if age:
                outstr += age if first else ', '+age
                first = False  # Regardless of whether we were first, this should be False now
            if subject_area:
                outstr += subject_area if first else ', '+subject_area
                first = False  # See previous comment
            if geography:
                outstr += geography if first else ', '+geography
                # `first` is no longer relevant
        outstr += ') '
        # We'll return to `source` after the senses
    outdict["senses"] = senses
    outstr += senses
    outstr = outstr.strip()  # Just make sure we're clean. We're breaking with the spacing slightly
    # to avoid adding a double period after the senses.
    if full_info:
        outstr += '. Source: '+source if outstr[-1] != '.' else ' Source: '+source
    return outdict

def _get_pronoun_dictionary(m: lookup.WordMatch):
    dict_results = {}
    entry = m.dl_entry
    infl_filt = MatchFilter(ages=['X'],frequencies=['X','A'],variants=[entry.variant,'0'])
    pinfl = definitions.PronounInfl(decl=entry.decl,number='S')
    matches = [p for p in definitions.inflections['PRON'] if pinfl.matches(p)]
    matches = [ma for ma in matches if infl_filt.check_inflection(ma,'PRON')]
    if matches:
        end1='' # sg nom 
        stem1=''
        end2='' # sg gen
        stem2=''
        for ma in matches:
            if ma.case == 'NOM' and not stem1:
                end1=ma.ending_uvij
                stem1=ma.stem
            elif ma.case == 'GEN' and not stem2:
                end2=ma.ending_uvij
                stem2=ma.stem
        if not stem1 and not stem2:
            for ma in matches:
                if ma.case == 'X':
                    end1 = ''
                    stem1 = '1'
        if not stem1:
            stem1='1'

        nom_stem = m.get_stem(stem1)
        if stem2:
            gen_stem = m.get_stem(stem2)
            dict_results["principal_parts"] = [nom_stem+end1, gen_stem+end2]
            dictstr = nom_stem+end1+', '+gen_stem+end2+' '
        else:
            dict_results["principal_parts"] = [nom_stem+end1]
            dictstr = nom_stem+end1+' '

        dict_results["senses"] = entry.senses
        dictstr += ''.join(entry.senses)

    return dict_results

def _get_adjective_dictionary(m: lookup.WordMatch):
    # Numeric declines like adjective

    # NOTE: Comparisons with adjectives are tricky, because there are two separate examples:
    # first, there are adjectives with 4 stems and a declension and variant like 1 1; then
    # e.g. the 4th stem is the superlative
    # second, there are adjectives with declension and variant like 0 0, for which only the
    # 4th stem is present, and therefore acts as the superlative (or comp.)
    # I've updated DICTLINE.GEN so that COMP and SUPER adjectives of declension 0 0 are
    # in the same stem slot
    entry = m.dl_entry
    dict_results = {}
    dictstr = ""
    matches = definitions.get_possible_inflections(entry,infl_ages=['X'],infl_frequencies=['A'])
    matches = [m for m in matches if m.number=='S' and m.case=='NOM']
    if entry.pos == 'ADJ':
        matches = [m for m in matches if m.comparison == 'POS']
    end1='' # sg nom masc
    stem1=''
    end2='' # sg nom fem
    stem2=''
    end3='' # sg nom neut
    stem3=''
    for ma in matches:
        if ma.gender == 'M' or ma.gender == 'X' or ma.gender == 'C' and not stem1:
            end1 = ma.ending_uvij
            stem1 = ma.stem
        if ma.gender == 'F' or ma.gender == 'C' and not stem2:
            end2 = ma.ending_uvij
            stem2 = ma.stem
        elif ma.gender == 'N' and not stem3:
            end3 = ma.ending_uvij
            stem3 = ma.stem
    if stem1 and not stem2 and not stem3:
        stem2 = stem1
        end2 = end1
        stem3 = stem1
        end3 = end1

    # For adjectives it's common for stems to be matching 
    if stem1 and stem2 and stem3:
        stem1 = m.get_stem(stem1)
        stem2 = m.get_stem(stem2)
        stem3 = m.get_stem(stem3)
        if stem1 == stem2 and stem1 == stem3:
            if end1:
                dict_results["principal_parts"] = [stem1+end1, stem1+end2, stem1+end3]
                dict_results["principal_parts_abbreviated"] = [stem1+end1, f"-{end2}", f"-{end3}"]
                dictstr += stem1+end1+' -'+end2+' -'+end3
            else:
                dict_results["principal_parts"] = [stem1]
                dictstr += stem1  # Single termination, we should technically get the genitive
            dictstr += ' '
        elif stem1 == stem2:
            dict_results["principal_parts"] = [stem1+end1, stem1+end3]
            dictstr += stem1+end1+' -'+end3
            dictstr += ' '
        else:
            dict_results["principal_parts"] = [stem1+end1, stem2+end2, stem3+end3]
            dictstr += stem1+end1+' '+stem2+end2+' '+stem3+end3
            dictstr += ' '
    else:
        dict_results["principal_parts"] = [m.match_stem+m.match_ending]
        dictstr += m.match_stem+m.match_ending+' '

    if entry.pos == 'ADJ':
        dictstr += 'adj'
    else:
        dictstr += 'num adj'

    dictstr += ' '
    dict_results["senses"] = entry.senses
    dictstr += ''.join(entry.senses)

    return dict_results

def getDict(m: lookup.WordMatch):

    entry = m.dl_entry

    result = {
        "string_result": lookup.get_dictionary_string(m),
        "part_of_speech": entry.pos
    }

    if entry.pos == 'N':
        noundict = _get_noun_dictionary(m)
        result = {**result, **noundict}
    elif entry.pos == 'V':
        verbdict = _get_verb_dictionary(m)
        result = {**result, **verbdict}
    elif entry.pos == 'ADJ' or entry.pos == 'NUM':
        adjdict = _get_adjective_dictionary(m)
        result = {**result, **adjdict}
    elif entry.pos in ['PRON','PACK']:
        pronoundict = _get_pronoun_dictionary(m)
        result = {**result, **pronoundict}

    elif entry.pos == 'CONJ':
        result["principal_parts"] = [m.dl_stem1]
        result["senses"] = entry.senses
    elif entry.pos == 'ADV':
        # TODO Add comparison
        result["principal_parts"] = [m.dl_stem1]
        result["senses"] = entry.senses
    elif entry.pos == 'PREP':
        # TODO Placeholder until I get the chance to properly format
        result["principal_parts"] = [m.dl_stem1]
        result["senses"] = entry.senses
    
    return result

def is_in_vocab_list(vocab_list, first_principal_part) -> bool:
    """
    So why da hell does utils.get_vocab_list use utils._process_vocab_list_opt() 
    to get the definitions of 1902 Latin words as LONG DEFINITION STRINGS (which
    which takes a LONG TIME as you can guess, approximately 2.1 seconds on my beefy
    computer) and then compare it to th definitions it generates of the inputted text?!
    
    That code is total shit. It is literally the most inefficient thing I would
    even be able to think of.

    So anyway, this code is a better way to check if the word is in the given vocab
    list. HOWEVER, it REQUIRES the given word to be its FIRST PRINCIPAL PART.
    """
    vocab = []
    if vocab_list is None:
        return False
    if vocab_list == 'llpsi':
        llpsi_fname = os.path.join(os.path.dirname(os.path.abspath(pwutils.__file__)), 'data/lingualatina_voclist.txt')
        with open(llpsi_fname, 'r', encoding='utf-8') as f:
            llpsi_text = f.readlines()
        vocab = [x.strip() for x in llpsi_text]
    elif vocab_list[-4:] == '.txt':
        with open(vocab_list, 'r', encoding='utf-8') as f:
            vl_text = f.readlines()
        vocab = [x.strip() for x in vl_text]

    if first_principal_part in vocab:
        return True
    
    return False

def get_vocab_list(text, filt=MatchFilter(), full_info=False, markdown_fmt=False, vocab_list=None):
    """
    My modification of pwutils.get_vocab_list().

    Take an arbitrarily long string (newlines and all) and process each word,
    then compile dictionary entries.

    vocab_list is used to remove well-known words. It can be a filename, a built-in vocab list from the following list:
        llpsi  -  Lingua Latina per se Illustrata: Familia Romana
    or it can be a list combining both.

    Return [definitions, missed words]
    definitions = {word in sentence: [vocab entries found]}
    """
    tlist = re.split('[, \n!.\-:;?=+/\'\"^\\]\\[]', text)
    tlist = [t.lower() for t in tlist if t and t.isalpha() and len(t) > 1]
    tlist = list(set(tlist))

    defs = {

    }
    missed = set()
    for w in tlist:
        # Patch the 'sum' problem for now...
        if w.replace('u','v').replace('i','j') in definitions.irreg_sum:
            sum_def = 'sum, esse, fui, futurus [irreg] to be, exist; (Medieval, in perfect tense) to go'
            if w in defs.keys():
                defs[w].append(sum_def)
            else:
                defs[w] = [sum_def]
        else:
            ms = lookup.match_word(w)
            if len(ms) == 0:
                missed.add(w)
            # filt.remove_substantives(ms)
            wdefns = []
            for m in ms:
                if filt.check_dictline_word(m.dl_entry):
                    d = getDict(m)
                    if d["string_result"] == "":
                        continue
                    if not is_in_vocab_list(vocab_list, d["principal_parts"][0]):
                        wdefns.append(d)

            for wdefn in wdefns:
                if wdefn != '' and not is_in_vocab_list(vocab_list, wdefn["principal_parts"][0]):
                    if w in defs.keys():
                        defs[w].append(wdefn)
                    else:
                        defs[w] = [wdefn]

    missed_sort = sorted(missed)

    return (defs, missed_sort)

def lookup_text(text, ignore_easy_vocab=False):
    vocab_list = None
    if ignore_easy_vocab:
        vocab_list="llpsi"
    vocab_list = get_vocab_list(text, filt=MatchFilter(), vocab_list=vocab_list)
    return vocab_list

if __name__ == '__main__':
    matches = lookup_text("""quidem""", ignore_easy_vocab=False)
    print(matches[0])
