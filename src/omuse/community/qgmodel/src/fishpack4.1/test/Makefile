SRC=tblktri.f tcblktri.f tcmgnbn.f tgenbun.f thstcrt.f thstcsp.f thstcyl.f \
    thstplr.f thstssp.f thw3crt.f thwscrt.f thwscsp.f thwscyl.f thwsplr.f \
    thwsssp.f tpois3d.f tpoistg.f tsepeli.f tsepx4.f

EXES=$(subst .f,.exe, $(SRC))

all : $(EXES)

$(EXES) : $(SRC)

%.exe : %.f
	rm -f $@
	$(FC) $(FCFLAGS) $< -o $@ -L../lib -l fishpack
	./$@


clean :
	rm -f $(EXES)
	rm -rf *.dSYM
