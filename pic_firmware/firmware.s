subtitle "Microchip MPLAB XC8 C Compiler v3.10 (Free license) build 20250813170317 Og9 "

pagewidth 120

	opt flic

	processor	18F85K22
include "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc\18f85k22.cgen.inc"
getbyte	macro	val,pos
	(((val) >> (8 * pos)) and 0xff)
endm
byte0	macro	val
	(getbyte(val,0))
endm
byte1	macro	val
	(getbyte(val,1))
endm
byte2	macro	val
	(getbyte(val,2))
endm
byte3	macro	val
	(getbyte(val,3))
endm
byte4	macro	val
	(getbyte(val,4))
endm
byte5	macro	val
	(getbyte(val,5))
endm
byte6	macro	val
	(getbyte(val,6))
endm
byte7	macro	val
	(getbyte(val,7))
endm
getword	macro	val,pos
	(((val) >> (8 * pos)) and 0xffff)
endm
word0	macro	val
	(getword(val,0))
endm
word1	macro	val
	(getword(val,2))
endm
word2	macro	val
	(getword(val,4))
endm
word3	macro	val
	(getword(val,6))
endm
gettword	macro	val,pos
	(((val) >> (8 * pos)) and 0xffffff)
endm
tword0	macro	val
	(gettword(val,0))
endm
tword1	macro	val
	(gettword(val,3))
endm
tword2	macro	val
	(gettword(val,6))
endm
getdword	macro	val,pos
	(((val) >> (8 * pos)) and 0xffffffff)
endm
dword0	macro	val
	(getdword(val,0))
endm
dword1	macro	val
	(getdword(val,4))
endm
clrc   macro
	bcf	status,0
endm
setc   macro
	bsf	status,0
endm
clrz   macro
	bcf	status,2
endm
setz   macro
	bsf	status,2
endm
skipnz macro
	btfsc	status,2
endm
skipz  macro
	btfss	status,2
endm
skipnc macro
	btfsc	status,0
endm
skipc  macro
	btfss	status,0
endm
pushw macro
	movwf postinc1
endm
pushf macro arg1
	movff arg1, postinc1
endm
popw macro
	movf postdec1,f
	movf indf1,w
endm
popf macro arg1
	movf postdec1,f
	movff indf1,arg1
endm
popfc macro arg1
	movff plusw1,arg1
	decfsz fsr1,f
endm
skiprom24 macro arg1
	btfsc arg1,7
endm
	global	__ramtop
	global	__accesstop
# 38 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PMD3 equ 0F16h ;# 
# 83 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PMD2 equ 0F17h ;# 
# 134 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PMD1 equ 0F18h ;# 
# 196 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PMD0 equ 0F19h ;# 
# 273 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PSTR3CON equ 0F1Ah ;# 
# 384 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PSTR2CON equ 0F1Bh ;# 
# 573 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TXREG2 equ 0F1Ch ;# 
# 593 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RCREG2 equ 0F1Dh ;# 
# 613 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SPBRG2 equ 0F1Eh ;# 
# 633 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SPBRGH2 equ 0F1Fh ;# 
# 653 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
BAUDCON2 equ 0F20h ;# 
# 776 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TXSTA2 equ 0F21h ;# 
# 903 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RCSTA2 equ 0F22h ;# 
# 1039 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ANCON2 equ 0F23h ;# 
# 1151 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ANCON1 equ 0F24h ;# 
# 1263 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ANCON0 equ 0F25h ;# 
# 1375 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
MEMCON equ 0F26h ;# 
# 1436 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ODCON3 equ 0F27h ;# 
# 1469 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ODCON2 equ 0F28h ;# 
# 1519 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ODCON1 equ 0F29h ;# 
# 1558 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
REFOCON equ 0F2Ah ;# 
# 1623 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPTMRS2 equ 0F2Bh ;# 
# 1657 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPTMRS1 equ 0F2Ch ;# 
# 1724 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPTMRS0 equ 0F2Dh ;# 
# 1806 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CM3CON equ 0F2Eh ;# 
# 1811 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CM3CON1 equ 0F2Eh ;# 
# 2058 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CM2CON equ 0F2Fh ;# 
# 2063 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CM2CON1 equ 0F2Fh ;# 
# 2310 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T8CON equ 0F36h ;# 
# 2381 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PR8 equ 0F37h ;# 
# 2401 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR8 equ 0F38h ;# 
# 2421 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T6CON equ 0F39h ;# 
# 2492 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PR6 equ 0F3Ah ;# 
# 2512 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR6 equ 0F3Bh ;# 
# 2532 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCP8CON equ 0F46h ;# 
# 2611 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR8 equ 0F47h ;# 
# 2618 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR8L equ 0F47h ;# 
# 2638 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR8H equ 0F48h ;# 
# 2658 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCP3CON equ 0F49h ;# 
# 2740 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR3 equ 0F4Ah ;# 
# 2747 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR3L equ 0F4Ah ;# 
# 2767 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR3H equ 0F4Bh ;# 
# 2787 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ECCP3DEL equ 0F4Ch ;# 
# 2857 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ECCP3AS equ 0F4Dh ;# 
# 2939 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCP2CON equ 0F4Eh ;# 
# 2944 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ECCP2CON equ 0F4Eh ;# 
# 3131 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR2 equ 0F4Fh ;# 
# 3138 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR2L equ 0F4Fh ;# 
# 3158 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR2H equ 0F50h ;# 
# 3178 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ECCP2DEL equ 0F51h ;# 
# 3183 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PWM2CON equ 0F51h ;# 
# 3316 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ECCP2AS equ 0F52h ;# 
# 3398 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PADCFG1 equ 0F53h ;# 
# 3453 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CM1CON equ 0F54h ;# 
# 3458 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CM1CON1 equ 0F54h ;# 
# 3733 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CTMUICON equ 0F55h ;# 
# 3809 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CTMUCONL equ 0F56h ;# 
# 3887 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CTMUCONH equ 0F57h ;# 
# 3944 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ALRMVAL equ 0F58h ;# 
# 3951 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ALRMVALL equ 0F58h ;# 
# 3971 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ALRMVALH equ 0F59h ;# 
# 3991 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ALRMRPT equ 0F5Ah ;# 
# 4061 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ALRMCFG equ 0F5Bh ;# 
# 4137 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RTCVAL equ 0F5Ch ;# 
# 4144 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RTCVALL equ 0F5Ch ;# 
# 4164 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RTCVALH equ 0F5Dh ;# 
# 4234 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RTCCAL equ 0F5Eh ;# 
# 4304 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RTCCFG equ 0F5Fh ;# 
# 4369 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIE6 equ 0F60h ;# 
# 4408 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
EEDATA equ 0F61h ;# 
# 4428 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
EEADR equ 0F62h ;# 
# 4448 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
EEADRH equ 0F63h ;# 
# 4468 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
OSCCON2 equ 0F64h ;# 
# 4508 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
BAUDCON1 equ 0F65h ;# 
# 4513 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
BAUDCTL equ 0F65h ;# 
# 4517 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
BAUDCON equ 0F65h ;# 
# 5015 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP2CON2 equ 0F66h ;# 
# 5193 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP2CON1 equ 0F67h ;# 
# 5313 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP2STAT equ 0F68h ;# 
# 5740 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP2ADD equ 0F69h ;# 
# 5810 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP2MSK equ 0F69h ;# 
# 5880 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP2BUF equ 0F6Ah ;# 
# 5900 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T4CON equ 0F6Bh ;# 
# 5971 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PR4 equ 0F6Ch ;# 
# 5991 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR4 equ 0F6Dh ;# 
# 6011 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCP7CON equ 0F6Eh ;# 
# 6090 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR7 equ 0F6Fh ;# 
# 6097 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR7L equ 0F6Fh ;# 
# 6117 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR7H equ 0F70h ;# 
# 6137 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCP6CON equ 0F71h ;# 
# 6216 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR6 equ 0F72h ;# 
# 6223 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR6L equ 0F72h ;# 
# 6243 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR6H equ 0F73h ;# 
# 6263 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCP5CON equ 0F74h ;# 
# 6342 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR5 equ 0F75h ;# 
# 6349 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR5L equ 0F75h ;# 
# 6369 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR5H equ 0F76h ;# 
# 6389 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCP4CON equ 0F77h ;# 
# 6468 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR4 equ 0F78h ;# 
# 6475 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR4L equ 0F78h ;# 
# 6495 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR4H equ 0F79h ;# 
# 6515 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T5GCON equ 0F7Ah ;# 
# 6619 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T5CON equ 0F7Bh ;# 
# 6721 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR5 equ 0F7Ch ;# 
# 6728 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR5L equ 0F7Ch ;# 
# 6748 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR5H equ 0F7Dh ;# 
# 6768 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
EECON2 equ 0F7Eh ;# 
# 6788 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
EECON1 equ 0F7Fh ;# 
# 6854 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PORTA equ 0F80h ;# 
# 7046 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PORTB equ 0F81h ;# 
# 7232 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PORTC equ 0F82h ;# 
# 7414 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PORTD equ 0F83h ;# 
# 7655 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PORTE equ 0F84h ;# 
# 8008 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PORTF equ 0F85h ;# 
# 8193 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PORTG equ 0F86h ;# 
# 8404 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PORTH equ 0F87h ;# 
# 8614 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PORTJ equ 0F88h ;# 
# 8726 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
LATA equ 0F89h ;# 
# 8838 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
LATB equ 0F8Ah ;# 
# 8950 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
LATC equ 0F8Bh ;# 
# 9062 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
LATD equ 0F8Ch ;# 
# 9174 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
LATE equ 0F8Dh ;# 
# 9286 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
LATF equ 0F8Eh ;# 
# 9388 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
LATG equ 0F8Fh ;# 
# 9464 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
LATH equ 0F90h ;# 
# 9576 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
LATJ equ 0F91h ;# 
# 9688 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TRISA equ 0F92h ;# 
# 9750 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TRISB equ 0F93h ;# 
# 9812 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TRISC equ 0F94h ;# 
# 9874 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TRISD equ 0F95h ;# 
# 9936 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TRISE equ 0F96h ;# 
# 9998 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TRISF equ 0F97h ;# 
# 10055 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TRISG equ 0F98h ;# 
# 10099 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TRISH equ 0F99h ;# 
# 10161 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TRISJ equ 0F9Ah ;# 
# 10223 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
OSCTUNE equ 0F9Bh ;# 
# 10293 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PSTR1CON equ 0F9Ch ;# 
# 10359 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIE1 equ 0F9Dh ;# 
# 10442 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIR1 equ 0F9Eh ;# 
# 10525 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
IPR1 equ 0F9Fh ;# 
# 10608 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIE2 equ 0FA0h ;# 
# 10680 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIR2 equ 0FA1h ;# 
# 10752 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
IPR2 equ 0FA2h ;# 
# 10824 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIE3 equ 0FA3h ;# 
# 10929 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIR3 equ 0FA4h ;# 
# 11002 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
IPR3 equ 0FA5h ;# 
# 11075 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIR6 equ 0FA6h ;# 
# 11114 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PSPCON equ 0FA7h ;# 
# 11153 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
HLVDCON equ 0FA8h ;# 
# 11223 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
IPR6 equ 0FA9h ;# 
# 11262 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T1GCON equ 0FAAh ;# 
# 11366 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RCSTA1 equ 0FABh ;# 
# 11371 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RCSTA equ 0FABh ;# 
# 11704 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TXSTA1 equ 0FACh ;# 
# 11709 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TXSTA equ 0FACh ;# 
# 11992 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TXREG1 equ 0FADh ;# 
# 11997 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TXREG equ 0FADh ;# 
# 12030 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RCREG1 equ 0FAEh ;# 
# 12035 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RCREG equ 0FAEh ;# 
# 12068 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SPBRG1 equ 0FAFh ;# 
# 12073 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SPBRG equ 0FAFh ;# 
# 12106 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T3GCON equ 0FB0h ;# 
# 12210 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T3CON equ 0FB1h ;# 
# 12321 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR3 equ 0FB2h ;# 
# 12328 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR3L equ 0FB2h ;# 
# 12348 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR3H equ 0FB3h ;# 
# 12368 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CMSTAT equ 0FB4h ;# 
# 12373 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CMSTATUS equ 0FB4h ;# 
# 12474 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CVRCON equ 0FB5h ;# 
# 12559 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIE4 equ 0FB6h ;# 
# 12609 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIR4 equ 0FB7h ;# 
# 12659 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
IPR4 equ 0FB8h ;# 
# 12717 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIE5 equ 0FB9h ;# 
# 12756 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PIR5 equ 0FBAh ;# 
# 12795 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCP1CON equ 0FBBh ;# 
# 12800 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ECCP1CON equ 0FBBh ;# 
# 12987 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR1 equ 0FBCh ;# 
# 12994 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR1L equ 0FBCh ;# 
# 13014 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
CCPR1H equ 0FBDh ;# 
# 13034 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ECCP1DEL equ 0FBEh ;# 
# 13039 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PWM1CON equ 0FBEh ;# 
# 13172 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ECCP1AS equ 0FBFh ;# 
# 13254 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ADCON2 equ 0FC0h ;# 
# 13325 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ADCON1 equ 0FC1h ;# 
# 13429 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ADCON0 equ 0FC2h ;# 
# 13554 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ADRES equ 0FC3h ;# 
# 13561 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ADRESL equ 0FC3h ;# 
# 13581 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
ADRESH equ 0FC4h ;# 
# 13601 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP1CON2 equ 0FC5h ;# 
# 13606 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSPCON2 equ 0FC5h ;# 
# 13955 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP1CON1 equ 0FC6h ;# 
# 13960 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSPCON1 equ 0FC6h ;# 
# 14193 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP1STAT equ 0FC7h ;# 
# 14198 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSPSTAT equ 0FC7h ;# 
# 14791 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP1ADD equ 0FC8h ;# 
# 14796 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSPADD equ 0FC8h ;# 
# 15029 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP1MSK equ 0FC8h ;# 
# 15099 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSP1BUF equ 0FC9h ;# 
# 15104 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SSPBUF equ 0FC9h ;# 
# 15137 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T2CON equ 0FCAh ;# 
# 15208 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PR2 equ 0FCBh ;# 
# 15228 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR2 equ 0FCCh ;# 
# 15248 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T1CON equ 0FCDh ;# 
# 15350 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR1 equ 0FCEh ;# 
# 15357 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR1L equ 0FCEh ;# 
# 15377 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR1H equ 0FCFh ;# 
# 15397 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
RCON equ 0FD0h ;# 
# 15550 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
WDTCON equ 0FD1h ;# 
# 15610 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
IPR5 equ 0FD2h ;# 
# 15706 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
OSCCON equ 0FD3h ;# 
# 15783 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
SPBRGH1 equ 0FD4h ;# 
# 15803 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
T0CON equ 0FD5h ;# 
# 15873 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR0 equ 0FD6h ;# 
# 15880 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR0L equ 0FD6h ;# 
# 15900 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TMR0H equ 0FD7h ;# 
# 15920 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
STATUS equ 0FD8h ;# 
# 15991 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
FSR2 equ 0FD9h ;# 
# 15998 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
FSR2L equ 0FD9h ;# 
# 16018 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
FSR2H equ 0FDAh ;# 
# 16025 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PLUSW2 equ 0FDBh ;# 
# 16045 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PREINC2 equ 0FDCh ;# 
# 16065 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
POSTDEC2 equ 0FDDh ;# 
# 16085 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
POSTINC2 equ 0FDEh ;# 
# 16105 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
INDF2 equ 0FDFh ;# 
# 16125 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
BSR equ 0FE0h ;# 
# 16132 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
FSR1 equ 0FE1h ;# 
# 16139 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
FSR1L equ 0FE1h ;# 
# 16159 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
FSR1H equ 0FE2h ;# 
# 16166 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PLUSW1 equ 0FE3h ;# 
# 16186 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PREINC1 equ 0FE4h ;# 
# 16206 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
POSTDEC1 equ 0FE5h ;# 
# 16226 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
POSTINC1 equ 0FE6h ;# 
# 16246 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
INDF1 equ 0FE7h ;# 
# 16266 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
WREG equ 0FE8h ;# 
# 16286 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
FSR0 equ 0FE9h ;# 
# 16293 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
FSR0L equ 0FE9h ;# 
# 16313 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
FSR0H equ 0FEAh ;# 
# 16320 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PLUSW0 equ 0FEBh ;# 
# 16340 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PREINC0 equ 0FECh ;# 
# 16360 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
POSTDEC0 equ 0FEDh ;# 
# 16380 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
POSTINC0 equ 0FEEh ;# 
# 16400 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
INDF0 equ 0FEFh ;# 
# 16420 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
INTCON3 equ 0FF0h ;# 
# 16532 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
INTCON2 equ 0FF1h ;# 
# 16625 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
INTCON equ 0FF2h ;# 
# 16742 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PROD equ 0FF3h ;# 
# 16749 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PRODL equ 0FF3h ;# 
# 16769 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PRODH equ 0FF4h ;# 
# 16789 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TABLAT equ 0FF5h ;# 
# 16811 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TBLPTR equ 0FF6h ;# 
# 16818 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TBLPTRL equ 0FF6h ;# 
# 16838 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TBLPTRH equ 0FF7h ;# 
# 16858 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TBLPTRU equ 0FF8h ;# 
# 16867 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PCLAT equ 0FF9h ;# 
# 16874 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PC equ 0FF9h ;# 
# 16881 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PCL equ 0FF9h ;# 
# 16901 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PCLATH equ 0FFAh ;# 
# 16921 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
PCLATU equ 0FFBh ;# 
# 16928 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
STKPTR equ 0FFCh ;# 
# 17002 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TOS equ 0FFDh ;# 
# 17009 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TOSL equ 0FFDh ;# 
# 17029 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TOSH equ 0FFEh ;# 
# 17049 "C:\Users\User\.mchp_packs\Microchip\PIC18F-K_DFP\1.17.312\xc8\pic\include\proc/pic18f85k22.h"
TOSU equ 0FFFh ;# 
	debug_source C
	FNROOT	_main
	global	_ANCON2
_ANCON2	set	0xF23
	global	_ANCON1
_ANCON1	set	0xF24
	global	_ANCON0
_ANCON0	set	0xF25
	global	_LATD
_LATD	set	0xF8C
	global	_LATB
_LATB	set	0xF8A
	global	_TRISD
_TRISD	set	0xF95
	global	_TRISB
_TRISB	set	0xF93
	global	_OSCCONbits
_OSCCONbits	set	0xFD3
; #config settings
	config pad_punits      = on
	config apply_mask      = off
	config ignore_cmsgs    = off
	config default_configs = off
	config default_idlocs  = off
	config RETEN = "OFF"
	config INTOSCSEL = "HIGH"
	config SOSCSEL = "DIG"
	config XINST = "OFF"
	config FOSC = "INTIO2"
	config PLLCFG = "OFF"
	config FCMEN = "OFF"
	config IESO = "OFF"
	config PWRTEN = "ON"
	config BOREN = "OFF"
	config BORV = "3"
	config WDTEN = "OFF"
	config MCLRE = "ON"
	config STVREN = "ON"
	config DEBUG = "OFF"
	file	"c:\Users\User\.gemini\antigravity\scratch\local_ai_gui\pic_firmware\firmware.s"
	line	#
psect	cinit,class=CODE,delta=1,reloc=2
global __pcinit
__pcinit:
global start_initialization
start_initialization:

global __initialization
__initialization:
psect cinit,class=CODE,delta=1
global end_of_initialization,__end_of__initialization

;End of C runtime variable initialization code

end_of_initialization:
__end_of__initialization:
movlb 0
goto _main	;jump to C main() function
psect	cstackCOMRAM,class=COMRAM,space=1,noexec,lowdata
global __pcstackCOMRAM
__pcstackCOMRAM:
?_main:	; 1 bytes @ 0x0
??_main:	; 1 bytes @ 0x0
	ds   2
;!
;!Data Sizes:
;!    Strings     0
;!    Constant    0
;!    Data        0
;!    BSS         0
;!    Persistent  0
;!    Stack       0
;!
;!Auto Spaces:
;!    Space          Size  Autos    Used
;!    COMRAM           95      2       2
;!    BANK0           160      0       0
;!    BANK1           256      0       0
;!    BANK2           256      0       0
;!    BANK3           256      0       0
;!    BANK4           256      0       0
;!    BANK5           256      0       0
;!    BANK6           256      0       0
;!    BANK7           256      0       0

;!
;!Pointer List with Targets:
;!
;!    None.


;!
;!Critical Paths under _main in COMRAM
;!
;!    None.
;!
;!Critical Paths under _main in BANK0
;!
;!    None.
;!
;!Critical Paths under _main in BANK1
;!
;!    None.
;!
;!Critical Paths under _main in BANK2
;!
;!    None.
;!
;!Critical Paths under _main in BANK3
;!
;!    None.
;!
;!Critical Paths under _main in BANK4
;!
;!    None.
;!
;!Critical Paths under _main in BANK5
;!
;!    None.
;!
;!Critical Paths under _main in BANK6
;!
;!    None.
;!
;!Critical Paths under _main in BANK7
;!
;!    None.

;;
;;Main: autosize = 0, tempsize = 2, incstack = 0, save=0
;;

;!
;!Call Graph Tables:
;!
;! ---------------------------------------------------------------------------------
;! (Depth) Function   	        Calls       Base Space   Used Autos Params    Refs
;! ---------------------------------------------------------------------------------
;! (0) _main                                                 2     2      0       0
;!                                              0 COMRAM     2     2      0
;! ---------------------------------------------------------------------------------
;! Estimated maximum stack depth 0
;! ---------------------------------------------------------------------------------
;!
;! Call Graph Graphs:
;!
;! _main (ROOT)
;!

;!Address spaces:

;!Name               Size   Autos  Total    Usage
;!BITCOMRAM           95      0       0      0.0%
;!BITBANK0           160      0       0      0.0%
;!BITBANK1           256      0       0      0.0%
;!BITBANK2           256      0       0      0.0%
;!BITBANK3           256      0       0      0.0%
;!BITBANK4           256      0       0      0.0%
;!BITBANK5           256      0       0      0.0%
;!BITBANK6           256      0       0      0.0%
;!BITBANK7           256      0       0      0.0%
;!BITBIGSFRh         117      0       0      0.0%
;!BITBIGSFRlh        100      0       0      0.0%
;!BITBIGSFRll         13      0       0      0.0%
;!COMRAM              95      2       2      2.1%
;!BANK0              160      0       0      0.0%
;!BANK1              256      0       0      0.0%
;!BANK2              256      0       0      0.0%
;!BANK3              256      0       0      0.0%
;!BANK4              256      0       0      0.0%
;!BANK5              256      0       0      0.0%
;!BANK6              256      0       0      0.0%
;!BANK7              256      0       0      0.0%
;!BIGRAM            2047      0       0      0.0%
;!STACK                0      0       0      0.0%
;!DATA                 0      0       2      0.0%

	global	_main

;; *************** function _main *****************
;; Defined at:
;;		line 32 in file "c:\Users\User\.gemini\antigravity\scratch\local_ai_gui\pic_firmware\main.c"
;; Parameters:    Size  Location     Type
;;		None
;; Auto vars:     Size  Location     Type
;;		None
;; Return value:  Size  Location     Type
;;                  1    wreg      void 
;; Registers used:
;;		wreg, status,2, status,0
;; Tracked objects:
;;		On entry : 0/0
;;		On exit  : 0/0
;;		Unchanged: 0/0
;; Data sizes:     COMRAM   BANK0   BANK1   BANK2   BANK3   BANK4   BANK5   BANK6   BANK7
;;      Params:         0       0       0       0       0       0       0       0       0
;;      Locals:         0       0       0       0       0       0       0       0       0
;;      Temps:          2       0       0       0       0       0       0       0       0
;;      Totals:         2       0       0       0       0       0       0       0       0
;;Total ram usage:        2 bytes
;; This function calls:
;;		Nothing
;; This function is called by:
;;		Startup code after reset
;; This function uses a non-reentrant model
;;
psect	text0,class=CODE,space=0,reloc=2,group=0
	file	"c:\Users\User\.gemini\antigravity\scratch\local_ai_gui\pic_firmware\main.c"
	line	32
global __ptext0
__ptext0:
psect	text0
	file	"c:\Users\User\.gemini\antigravity\scratch\local_ai_gui\pic_firmware\main.c"
	line	32
	
_main:
;incstack = 0
	callstack 31
	line	34
	
l812:
	movlw	(07h & ((1<<3)-1))<<4
	iorwf	((c:4051))^0f00h,c	;volatile
	line	35
	movlw	((0 & ((1<<2)-1))<<0)|not (((1<<2)-1)<<0)
	andwf	((c:4051))^0f00h,c	;volatile
	line	38
	
l814:
	movlb	15	; () banked
	clrf	((3877))&0ffh	;volatile
	line	39
	
l816:; BSR set to: 15

	clrf	((3876))&0ffh	;volatile
	line	40
	
l818:; BSR set to: 15

	clrf	((3875))&0ffh	;volatile
	line	43
	
l820:; BSR set to: 15

	clrf	((c:3987))^0f00h,c	;volatile
	line	44
	
l822:; BSR set to: 15

	clrf	((c:3989))^0f00h,c	;volatile
	line	45
	
l824:; BSR set to: 15

	clrf	((c:3978))^0f00h,c	;volatile
	line	46
	
l826:; BSR set to: 15

	clrf	((c:3980))^0f00h,c	;volatile
	line	49
	
l828:
	comf	((c:3978))^0f00h,c	;volatile
	line	50
	
l830:
	comf	((c:3980))^0f00h,c	;volatile
	line	51
	
l832:
	asmopt push
asmopt off
movlw  11
movwf	(??_main+0+1)^00h,c
movlw	38
movwf	(??_main+0)^00h,c
	movlw	94
u17:
decfsz	wreg,f
	bra	u17
	decfsz	(??_main+0)^00h,c,f
	bra	u17
	decfsz	(??_main+0+1)^00h,c,f
	bra	u17
asmopt pop

	goto	l828
	global	start
	goto	start
	callstack 0
	line	53
GLOBAL	__end_of_main
	__end_of_main:
	signat	_main,89
psect	smallconst,class=SMALLCONST,space=0,reloc=2,noexec
global __psmallconst
__psmallconst:
	db	0
	db 0	; dummy byte at the end
	global	__smallconst
__smallconst	set	__psmallconst
	global	__mediumconst
__mediumconst	set	__psmallconst
	GLOBAL	__activetblptr
__activetblptr	EQU	0
	psect	intsave_regs,class=BIGRAM,space=1,noexec
	PSECT	rparam,class=COMRAM,space=1,noexec
	GLOBAL	__Lrparam
	FNCONF	rparam,??,?
	GLOBAL	___rparam_used
	___rparam_used EQU 1
	GLOBAL	___param_bank
	___param_bank EQU 0
GLOBAL	__Lparam, __Hparam
GLOBAL	__Lrparam, __Hrparam
__Lparam	EQU	__Lrparam
__Hparam	EQU	__Hrparam
	end
