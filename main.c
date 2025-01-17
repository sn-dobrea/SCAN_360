#include "timer_b.h"
#include <msp430.h>

void config_CS_20MHz(void);
void config_CS_Pins(void);

void config_UART_to_Pc(void);
void config_UART_to_Pc_Pins(void);

void config_UART_to_LIDAR(void);
void config_UART_to_LIDAR_Pins(void);

void config_Timer_PWM_for_servo(void);
// void config_Second_Timer_B(void);

volatile int pwm_value = 10200;
volatile int direction = 1;


volatile unsigned char get_sample_rate[2]={0xA5,0x59}; // get sample rate request
volatile unsigned char get_health_status[2]={0xA5,0x52}; // get health request
volatile unsigned char stop_scan[2]={0xA5,0x25}; // stop scan request
volatile unsigned char reset_scan[2]={0xA5,0x40}; // reset request
volatile unsigned char start_scan[2]={0xA5,0x20}; // start scan request

const int angles[] = {   0x2710, 0x27EE, 0x28CC, 0x29AA, 0x2A88, 0x2B66, 0x2C44, 0x2D22,
                        0x2E00, 0x2EDE, 0x2FBC, 0x309A, 0x3178, 0x3256, 0x3334, 0x3412,
                        0x34F0, 0x35CE, 0x36AC, 0x378A, 0x3868, 0x3946, 0x3A24, 0x3B02,
                        0x3BE0, 0x3CBE, 0x3D9C, 0x3E7A, 0x3F58, 0x4036, 0x4114, 0x41F2,
                        0x42D0, 0x43AE, 0x448C, 0x456A, 0x4648, 0x4726, 0x4804, 0x48E2,
                        0x49C0, 0x4A9E, 0x4B7C, 0x4C5A, 0x4D38, 0x4E16, 0x4EF4, 0x4FD2,
                        0x50B0, 0x518E, 0x526C, 0x534A, 0x5428, 0x5506, 0x55E4, 0x56C2,
                        0x57A0, 0x587E, 0x595C, 0x5A3A, 0x5B18, 0x5BF6, 0x5CD4, 0x5DB2,
                        0x5E90, 0x5F6E, 0x604C, 0x612A, 0x6208, 0x62E6, 0x63C4, 0x64A2,
                        0x6580, 0x665E, 0x673C, 0x681A, 0x68F8, 0x69D6, 0x6AB4, 0x6B92,
                        0x6C70, 0x6D4E, 0x6E2C, 0x6F0A, 0x6FE8, 0x70C6, 0x71A4, 0x7282,
                        0x7360, 0x743E, 0x751C, 0x75FA, 0x76D8, 0x77B6, 0x7894, 0x7972,
                        0x7A50, 0x7B2E, 0x7C0C, 0x7CEA, 0x7DC8, 0x7EA6, 0x7F84, 0x8062,
                        0x8140, 0x821E, 0x82FC, 0x83DA, 0x84B8, 0x8596, 0x8674, 0x8752,
                        0x8830, 0x890E, 0x89EC, 0x8ACA, 0x8BA8, 0x8C86, 0x8D64, 0x8E42,
                        0x8F20, 0x8FFE, 0x90DC, 0x91BA, 0x9298, 0x9376, 0x9454, 0x9532,
                        0x9610, 0x96EE, 0x97CC, 0x98AA, 0x9988, 0x9A66, 0x9B44, 0x9C22,
                        0x9D00, 0x9DDE, 0x9EBC, 0x9F9A, 0xA078, 0xA156, 0xA234, 0xA312,
                        0xA3F0, 0xA4CE, 0xA5AC, 0xA68A, 0xA768, 0xA846, 0xA924, 0xAA02,
                        0xAAE0, 0xABBE, 0xAC9C, 0xAD7A, 0xAE58, 0xAF36, 0xB014, 0xB0F2,
                        0xB1D0, 0xB2AE, 0xB38C, 0xB46A, 0xB548, 0xB626, 0xB704, 0xB7E2,
                        0xB8C0, 0xB99E, 0xBA7C, 0xBB5A, 0xBC38, 0xBD16, 0xBDF4, 0xBED2,
                        0xBFB0, 0xC08E, 0xC16C, 0xC24A, 0xC328};

unsigned int data;
unsigned int i;

// The main function initializes all hardware components and enables global interrupts.
// Calls the configuration functions and remains in a low-power state waiting for events.
int main(void)
{
    config_CS_20MHz();
    
    config_UART_to_Pc();

    config_UART_to_LIDAR();

    config_Timer_PWM_for_servo();
    // config_Second_Timer_B();


    __bis_SR_register(GIE);
    PM5CTL0 &= ~LOCKLPM5;
    __no_operation();
}


// Configures the system clock to operate at 20 MHz.
// Sets the reference source, dividers, and DCO (Digitally Controlled Oscillator) for different clocks (ACLK, MCLK, SMCLK).
void config_CS_20MHz(void)
{
    WDTCTL = WDTPW | WDTHOLD;                                   // Stop WDT
    FRCTL0 = FRCTLPW | NWAITS_2;
    __bis_SR_register(SCG0);                                    // disable FLL
    CSCTL3 |= SELREF__REFOCLK;                                  // Set REFO as FLL reference source
    CSCTL0 = 0;                                                 // clear DCO and MOD registers
    CSCTL1 = DCOFTRIMEN_1 | DCOFTRIM0 | DCOFTRIM1 | DCORSEL_6;  // DCOFTRIM=3, DCO Range = 20MHz
    CSCTL2 = FLLD_0 + 610;                                      // DCOCLKDIV
    __delay_cycles(3);
    __bic_SR_register(SCG0);                                    // enable FLL
    while(CSCTL7 & (FLLUNLOCK0 | FLLUNLOCK1));                  // FLL locked

    CSCTL4 = SELMS__DCOCLKDIV | SELA__REFOCLK;                  // set default REFO(~32768Hz) as ACLK source, ACLK = 32768Hz
                                                                // default DCOCLKDIV as MCLK and SMCLK source
    CSCTL5 |= DIVM_0 | DIVS_0;                                  // MCLK and SMCLK divider

    config_CS_Pins();
}


// Configures the pins to output the system clock.
void config_CS_Pins(void)
{ 
    P3DIR   |=  BIT0 | BIT4;
    P3SEL0  |=  BIT0 | BIT4;

}


// Configures the UART A1 module for communication with the PC (baud rate, operating mode).
// Includes setting the transmission speed and enabling interrupts for UART operations.
void config_UART_to_Pc(void)
{
    config_UART_to_Pc_Pins();

    UCA1CTLW0 |= UCSWRST;
    UCA1CTLW0 |= UCSSEL_2;

    UCA1BR0 = 0x0A;                                             // UCBRx = 0x0A
    UCA1BR1 = 0x00;
    UCA1MCTLW = 0xADD1;                                         // UCBRSx = 0xAD, UCBRFx = 0x0D, OS16 = 1

    UCA1CTLW0 &= ~UCSWRST;
    UCA1IE |= UCRXIE;
}


// Sets up pins P4.2 and P4.3 for UART communication (TX and RX) with the PC.
void config_UART_to_Pc_Pins(void)
{
    P4SEL0  |= BIT2 | BIT3;
}


// Configures the UART A0 module for communication with the LIDAR.
// Sets the transmission speed and other necessary UART registers.
void config_UART_to_LIDAR(void)
{
    config_UART_to_LIDAR_Pins();

    UCA0CTLW0 |= UCSWRST;
    UCA0CTLW0 |= UCSSEL_2;

    UCA0BR0 = 0x0A;                                             // UCBRx = 0x0A
    UCA0BR1 = 0x00;
    UCA0MCTLW = 0xADD1;                                         // UCBRSx = 0xAD, UCBRFx = 0x0D, OS16 = 1

    UCA0CTLW0 &= ~UCSWRST;
    UCA0IE |= UCRXIE;
}


// Sets up pins P1.6 and P1.7 for UART communication (TX and RX) with the LIDAR sensor.
void config_UART_to_LIDAR_Pins(void)
{
    P1SEL0 |= BIT6 | BIT7;
}


// Configures the PWM (Pulse Width Modulation) for controlling a servo motor.
// Sets the PWM period and duty cycle (pulse width) for servo position control.
void config_Timer_PWM_for_servo(void)
{
    P5DIR |= BIT0;                     // P5.0 output
    P5SEL0 |= BIT0;                    // P5.0 options select

    TB2CCR0 = 60000-1;                          // PWM Period
    TB2CCTL1 = OUTMOD_7;                        // CCR1 reset/set
    TB2CCR1 = pwm_value;                        // CCR1 PWM duty cycle
    TB2CTL = TBSSEL__SMCLK | MC__UP | TBCLR;    // SMCLK, up mode, clear TBR
}


// Interrupt service routine for the UART A1 module (communication with the PC).
// Processes incoming data to control the servo motor or send commands to the LIDAR sensor.
#pragma vector=USCI_A1_VECTOR
__interrupt void USCI_A1_ISR(void)
{
  switch(__even_in_range(UCA1IV,USCI_UART_UCTXCPTIFG))
  {
    case USCI_NONE: break;
    case USCI_UART_UCRXIFG:
        while(!(UCA1IFG & UCTXIFG));
        data = UCA1RXBUF;
        
        if (data <= 180) 
        {
            TB2CCR1 = angles[data];
        }
        else if (data == 0xFF)
        {
            for(i=0;i<2;i++)
            {
                while(!(UCA0IFG&UCTXIFG));// verifica daca nu se transmite ceva
                UCA0TXBUF = get_health_status[i];
            }
        }
        else if (data == 0xEE)
        {
            for(i=0;i<2;i++)
            {
                while(!(UCA0IFG&UCTXIFG));// verifica daca nu se transmite ceva
                UCA0TXBUF = start_scan[i];
            }
        }
        else if (data == 0xDD)
        {
            for(i=0;i<2;i++)
            {
                while(!(UCA0IFG&UCTXIFG));// verifica daca nu se transmite ceva
                UCA0TXBUF = stop_scan[i];
            }
        }
        else
        {
            // while(!(UCA0IFG&UCTXIFG));// verifica daca nu se transmite ceva
            // UCA0TXBUF = data;
            // ++idx;
        }

        __no_operation();
        break;
    case USCI_UART_UCTXIFG: break;
    case USCI_UART_UCSTTIFG: break;
    case USCI_UART_UCTXCPTIFG: break;
    default: break;
  }
}


// Interrupt service routine for the UART A0 module (communication with the LIDAR ).
// Forwards received packets from the LIDAR to the PC for further processing.
#pragma vector=USCI_A0_VECTOR
__interrupt void USCI_A0_ISR(void)
{
  switch(__even_in_range(UCA0IV,USCI_UART_UCTXCPTIFG))
  {
    case USCI_NONE: break;
    case USCI_UART_UCRXIFG:
     while(!(UCA1IFG&UCTXIFG));// verifica daca poate transmite catre PC
     UCA1TXBUF = UCA0RXBUF;// transmite catre PC pachetul receptionat de la LIDAR
      __no_operation();
      break;
    case USCI_UART_UCTXIFG: break;
    case USCI_UART_UCSTTIFG: break;
    case USCI_UART_UCTXCPTIFG: break;
    default: break;
  }
}
