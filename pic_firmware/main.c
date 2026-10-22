#include <xc.h>

// CONFIG1L
#pragma config RETEN = OFF      // Ultra low-power regulator disabled
#pragma config INTOSCSEL = HIGH // High-power mode during Sleep
#pragma config SOSCSEL = DIG    // Digital (SCLKI) mode
#pragma config XINST = OFF      // Extended Instruction Set disabled

// CONFIG1H
#pragma config FOSC = INTIO2    // Internal oscillator block, port function on RA6 and RA7
#pragma config PLLCFG = OFF     // PLL disabled
#pragma config FCMEN = OFF      // Fail-Safe Clock Monitor disabled
#pragma config IESO = OFF       // Internal/External Oscillator Switchover disabled

// CONFIG2L
#pragma config PWRTEN = ON      // Power-up Timer enabled
#pragma config BOREN = OFF      // Brown-out Reset disabled
#pragma config BORV = 3         // Brown-out Reset Voltage (1.8V)

// CONFIG2H
#pragma config WDTEN = OFF      // Watchdog Timer disabled

// CONFIG3H
#pragma config MCLRE = ON       // MCLR pin enabled, RG5 input pin disabled

// CONFIG4L
#pragma config STVREN = ON      // Stack Full/Underflow will cause Reset
#pragma config DEBUG = OFF      // Background Debugger disabled

#define _XTAL_FREQ 16000000

void main(void) {
    // Configure internal oscillator to 16MHz
    OSCCONbits.IRCF = 0b111;    // 16 MHz HFINTOSC
    OSCCONbits.SCS = 0b00;      // Primary clock

    // Configure all analog pins as digital I/O
    ANCON0 = 0x00;
    ANCON1 = 0x00;
    ANCON2 = 0x00;

    // Set PORTB and PORTD as output
    TRISB = 0x00;
    TRISD = 0x00;
    LATB = 0x00;
    LATD = 0x00;

    while (1) {
        LATB = ~LATB;           // Toggle all PORTB pins (RB0-RB7)
        LATD = ~LATD;           // Toggle all PORTD pins (RD0-RD7)
        __delay_ms(500);        // 500ms delay (1 Hz blink)
    }
}
