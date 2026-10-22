/*
 * ===================================================================
 * MICROCHIP PIC18F85K22 DEVELOPMENT BOARD — 8-BIT LCD DRIVER TEMPLATE
 * File: LCD_PT2.c
 * ===================================================================
 * Target MCU : PIC18F85K22
 * Clock      : 4.9152 MHz (f_osc)
 * -------------------------------------------------------------------
 * LCD HARDWARE MAPPING:
 *   RH0..RH7 --> LCD Data Lines D0..D7 (PORTH, 8-Bit Bus)
 *   RE1      --> LCD Enable Line (EN)
 *   RE0      --> LCD RS (Register Select) Line
 *   RA4      --> LCD Backlight Control (High = ON)
 * ===================================================================
 */

#include <xc.h>
#include <stdint.h>

#pragma config XINST = OFF      // Extended Instruction Set Disabled
#pragma config FOSC = HS1       // High-Speed Crystal Oscillator (4.9152 MHz)
#pragma config WDTEN = OFF      // Watchdog Timer Disabled
#pragma config CP0 = OFF        // Code Protect Disabled
#pragma config BOREN = ON       // Brown-out Reset Enabled
#pragma config PWRTEN = ON      // Power-up Timer Enabled
#pragma config PBADEN = OFF     // Digital I/O on PORTB

#define _XTAL_FREQ 4915200UL    // 4.9152 MHz External Crystal

// LCD Signal Definitions
#define LCD_DATA_PORT LATH       // PORTH (RH0..RH7) -> LCD D0..D7
#define LCD_DATA_TRIS TRISH      // PORTH Data Direction Register
#define LCD_RS        LATEbits.LATE0 // RE0 -> RS (0=Command, 1=Data)
#define LCD_EN        LATEbits.LATE1 // RE1 -> EN (Enable Pulse)
#define LCD_BACKLIGHT LATAbits.LATA4 // RA4 -> Backlight (1=ON, 0=OFF)

// -------------------------------------------------------------------
// LCD HARDWARE LOW-LEVEL DRIVER SUBROUTINES
// -------------------------------------------------------------------
void LCD_Pulse_Enable(void) {
    LCD_EN = 1;
    __delay_us(10);
    LCD_EN = 0;
    __delay_us(100);
}

void LCD_Cmd(uint8_t cmd) {
    LCD_RS = 0;             // Select Command Register
    LCD_DATA_PORT = cmd;    // Output 8-bit Command Byte onto PORTH
    LCD_Pulse_Enable();
    if (cmd == 0x01 || cmd == 0x02) {
        __delay_ms(2);      // Extended delay for Clear / Home commands
    }
}

void LCD_Char(char data) {
    LCD_RS = 1;             // Select Data Register
    LCD_DATA_PORT = data;   // Output 8-bit Data Byte onto PORTH
    LCD_Pulse_Enable();
}

void LCD_String(const char *str) {
    while (*str) {
        LCD_Char(*str++);
    }
}

void LCD_Set_Cursor(uint8_t row, uint8_t col) {
    uint8_t address = (row == 1) ? (0x80 + (col - 1)) : (0xC0 + (col - 1));
    LCD_Cmd(address);
}

void LCD_Init(void) {
    // Configure I/O Ports
    ANCON0 = 0x00; ANCON1 = 0x00; ANCON2 = 0x00; // Digital I/O
    
    LCD_DATA_TRIS = 0x00; // PORTH as Outputs (Data Lines D0-D7)
    TRISEbits.TRISE0 = 0; // RE0 as Output (RS)
    TRISEbits.TRISE1 = 0; // RE1 as Output (EN)
    TRISAbits.TRISA4 = 0; // RA4 as Output (Backlight)
    
    LCD_RS = 0;
    LCD_EN = 0;
    LCD_BACKLIGHT = 1;    // Turn ON LCD Backlight
    
    __delay_ms(50);       // Wait for LCD Controller Power-Up
    
    // 8-Bit Initialization Sequence
    LCD_Cmd(0x38); // Function Set: 8-bit Mode, 2 Lines, 5x8 Font
    LCD_Cmd(0x0C); // Display Control: Display ON, Cursor OFF, Blink OFF
    LCD_Cmd(0x01); // Clear Display
    LCD_Cmd(0x06); // Entry Mode: Increment Cursor, No Shift
    __delay_ms(5);
}

// -------------------------------------------------------------------
// MAIN DEMO FUNCTION
// -------------------------------------------------------------------
void main(void) {
    LCD_Init();
    
    LCD_Set_Cursor(1, 1);
    LCD_String("PIC18F85K22 MCU");
    
    LCD_Set_Cursor(2, 1);
    LCD_String("LCD_PT2 4.9152M");
    
    while (1) {
        // Main Loop
    }
}
