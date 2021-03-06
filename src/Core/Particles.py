#!/usr/bin/env python
from sympy import Symbol, Rational, I, sqrt
import sys

sys.path.append('./GroupTheory')
from Contraction import GetDynkinLabel, getdimIrrep
from numpy import matrix as npa
from sympy.parsing.sympy_parser import parse_expr
import copy


class particle(object):

    def __init__(self, name, dic, Groups, idb, FromCplx=False):
        if type(name) != Symbol:
            self._name = Symbol(name)
        else:
            self._name = name
        self.idb = idb
        self.Qnb = self.getQnb(dic['Qnb'], Groups)
        self.mapQ = {}
        self.Q = self.buildupQ(Groups)
        self.W = 0
        self.lnQ = len(self.Q)
        self.Gen = self.getGen(dic)
        self.Cplx = False
        self.FromCplx = FromCplx
        self.rangeindices = self.get_RangeIndices(Groups)

    def __repr__(self):
        return "{}".format(self._name)

    def getGen(self, dic):
        """convert the Gen into either a symbol or a number"""
        try:
            return Symbol(dic['Gen'])
        except:
            return int(dic['Gen'])

    def buildupQ(self, Groups):
        """Construct the Q vector of charges under the U1 sector treated as a whole. New in version 2 """
        out = []
        ic = 0
        for gg, val, U in Groups:
            if U:
                out.append(self.Qnb[gg])
                self.mapQ[gg] = ic
                ic += 1
        return npa(out).transpose()

    def getQnb(self, dic, Groups):
        """Get the Qnbs of the particle from the dic. The only thing to do is to transform the DimR notation into DynkinLabels"""
        # PB is that I cannot manage to triger on the Integer type of sympy
        for key, val in dic.items():
            if type(val) == str:
                try:
                    val = Rational(val)
                except TypeError:
                    val = parse_expr(val.replace('i','I').replace('Sqrt','sqrt'))
                except:
                    exit("Error, converting qnb of `{}: {}`".format(key,val))
                dic[key] = val
            if type(val) == tuple:
                pass
            elif type(val) == Rational:
                assert [el[2] for el in Groups if el[0] == key][0]  # check that the group is U1 factor indeed
            elif not ([el[2] for el in Groups if el[0] == key][0]):
                dic[key] = GetDynkinLabel([el[1]._absname for el in Groups if el[0] == key][0], val, self.idb)
        if Groups[-1][0] == 'SUndum':
            dic[Groups[-1][0]] = Groups[-1][1].Dynksinglet
        return dic

    def get_RangeIndices(self, Groups):
        temp = {}
        for group in Groups:
            if not (group[1].U):
                temp[group[0]] = getdimIrrep(self.Qnb[group[0]], group[1], self.idb)
        return temp

    def isCharged(self, group, Dynkin=False):
        """check if the particle is charge under the group object"""
        if not (Dynkin):
            return not (self.Qnb[group.name] == int(group.singlet))
        else:
            return not (self.Qnb[group.name] == group.Dynksinglet)


class higgsField(particle):
    def __init__(self, name, dic, Groups, idb):
        self._name = Symbol(name)
        self.RealFields = dic['RealFields']
        self.RealComponents = []
        self.getRealFields()
        # call the particle constructor
        self.norm = dic['Norm']
        dic['Gen'] = 1
        self.idb = idb
        particle.__init__(self, name, dic, Groups, self.idb)
        self.Cplx = True  # has to be after the particle constructor otherwise it is overwriten

    def getRealFields(self):
        """return the field """
        if self.RealFields[1] == 0: #This is used to implement adjoint transforming under the conjugate matrix
            fieldssplitted = self.RealFields[0].split('I'), 0
        else:
            fieldssplitted = self.RealFields[0].split('I'), self.RealFields[1].split('I')  # if there is a I in the real field name it crashes...

        for fieldsplitted in fieldssplitted:
            if fieldsplitted == 0:
                self.CplxPart = 0
                self.Coeff = 0
            elif len(fieldsplitted) == 1:
                self.RealPart = Symbol(fieldsplitted[0])
                self.RealComponents.append(Symbol(fieldsplitted[0]))
            else:
                assert len(fieldsplitted) == 2
                if fieldsplitted[0] == '':
                    self.CplxPart = Symbol(fieldsplitted[1][1:])
                    self.RealComponents.append(I * Symbol(fieldsplitted[1][1:]))
                    self.Coeff = I
                elif fieldsplitted[0] == '-':
                    self.CplxPart = Symbol(fieldsplitted[1][1:])
                    self.RealComponents.append(-I * Symbol(fieldsplitted[1][1:]))
                    self.Coeff = -I
                elif fieldsplitted[0] == '+':
                    self.CplxPart = Symbol(fieldsplitted[1][1:])
                    self.RealComponents.append(I * Symbol(fieldsplitted[1][1:]))
                    self.Coeff = I
                else:
                    exit("Error while transforming complex field {}".format(self.RealFields))
