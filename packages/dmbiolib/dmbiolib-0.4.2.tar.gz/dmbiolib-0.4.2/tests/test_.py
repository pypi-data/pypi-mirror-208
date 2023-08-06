#!/usr/bin/env python
import pytest
dbl=__import__('dmbiolib')

def test_check_file():
    assert not dbl.check_file('%1@3$9)*+7',False)

def test_check_plot_format():
    assert dbl.check_plot_format('png')

def test_check_seq():
    assert dbl.check_seq('gacgagt',dbl.dna,dbl.dna)==(True,True)

def test_complexity():
    assert dbl.complexity('atgdbctss')==[{'M': 1},{'F': 1, 'C': 1, 'S': 2, 'V': 1, 'G': 1, 'A': 1, 'I': 1, 'T': 1},{'W': 1, 'C': 1, 'S': 2}]

def test_compress():
    assert dbl.compress('aatggnngcc')=='atgnngc'

def test_diff():
    assert dbl.diff(['agct','gatc','ctga','aata'])==2

def test_entropy():
    assert dbl.entropy([[1,1,0],[0,1,2],[1,2,1]])==-4.0

def test_exprange():
    assert list(dbl.exprange(1,100,3))==[1,3,9,27,81]

def test_find_ambiguous():
    assert dbl.find_ambiguous('gatcgatcgtnnnnngactgavvmttcgsbynccgtcga')=={10: 5, 21: 3, 28: 4}

def test_format_dna():
    assert dbl.format_dna('gatcgatcgatcgatcgtacgtatcgat',5,30,10)=='             10        20\n     gatcgatcgatcgatcgtacgtatcgat\n'

def test_intorfloat():
    assert dbl.intorfloat('3424.323')=='float'

def test_match():
    assert dbl.match('acgatcg','acsancg')

def test_mean():
    assert dbl.mean([12,30,24])==22.0

def test_nt_match():
    assert dbl.nt_match('s','n')

def test_prefix():
    assert dbl.prefix(['P0-left_L4_2.fq.gz', 'P0-right_L4_2.fq.gz'])==[7, 8]

def test_revcomp():
    assert dbl.revcomp('agctgctaa')=='ttagcagct'

def test_transl():
    assert dbl.transl('atgctgaaagcc')=='MLKA'

pytest.main()
