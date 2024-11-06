#include <msp430.h>


volatile int direction = 1; // 1 pentru crestere, -1 pentru scadere
volatile int pwm_value = 510;

void Configure_Clocks_24MHz(void)
{
    WDTCTL = WDTPW | WDTHOLD;                 // Stop WDT
//    FRCTL0 = FRCTLPW | NWAITS_2;
    __bis_SR_register(SCG0);                                    // disable FLL
    CSCTL3 |= SELREF__REFOCLK;                                  // Set REFO as FLL reference source
    CSCTL0 = 0;                                                 // clear DCO and MOD registers
    CSCTL1 = DCOFTRIMEN_1 | DCOFTRIM0 | DCOFTRIM1 | DCORSEL_0;  // DCOFTRIM=3, DCO Range = 1MHz
    CSCTL2 = FLLD_0 + 30;                                       // DCOCLKDIV
    __delay_cycles(3);
    __bic_SR_register(SCG0);                                    // enable FLL
    while(CSCTL7 & (FLLUNLOCK0 | FLLUNLOCK1));                  // FLL locked

    CSCTL4 = SELMS__DCOCLKDIV | SELA__REFOCLK;                  // set default REFO(~32768Hz) as ACLK source, ACLK = 32768Hz
                                                                // default DCOCLKDIV as MCLK and SMCLK source
    CSCTL5 |= DIVM_0 | DIVS_0;                                  // MCLK and SMCLK divider
}

void Configure_P1_6(void)
{
    P1DIR |= BIT6;                     // P1.6 output
    P1SEL1 |= BIT6;                    // P1.6 options select

    // Disable the GPIO power-on default high-impedance mode to activate
    // previously configured port settings
    PM5CTL0 &= ~LOCKLPM5;
}

void Configure_Timer(void)
{
    TB0CCR0 = 3050-1;                         // PWM Period
    TB0CCTL1 = OUTMOD_7;                      // CCR1 reset/set
    TB0CCR1 = pwm_value;                            // CCR1 PWM duty cycle
    TB0CTL = TBSSEL__SMCLK | MC__UP | TBCLR;  // SMCLK, up mode, clear TBR
}

void Configure_Second_Timer_B(void)
{
    // Configuram Timer_B1 pentru a genera Intreruperi la fiecare secunda
    TB1CCR0 = 32768-1;                        // Setam perioada la 1 secunda, ACLK = 32.768kHz
    TB1CCTL0 = CCIE;                          // Activam Intreruperea pentru CCR0
    TB1CTL = TBSSEL__ACLK | MC__UP | TBCLR;   // ACLK, up mode, clear TBR
}






int main(void)
{
    Configure_Clocks_24MHz();
    Configure_P1_6();
    Configure_Timer();
    Configure_Second_Timer_B();


    __bis_SR_register(LPM0_bits| GIE);             // Enter LPM0
    __no_operation();                         // For debugger
}

// ISR pentru Timer_B (la fiecare secunda)
#pragma vector = TIMER1_B0_VECTOR
__interrupt void Timer_B(void)
{
//      if(pwm_value == 500){
//          pwm_value=2500;
//      }
//      else{
//          pwm_value = 500;
//      }
    // Modificam PWM-ul Intre 510 si 2500
    pwm_value += 11 * direction;

    if (pwm_value >= 2500) {
        direction = -1;  // Incepem sa scadem
    } else if (pwm_value <= 510) {
        direction = 1;   // Incepem sa crestem
    }

    TB0CCR1 = pwm_value; // Actualizam valoarea pentru duty cycle-ul PWM
}
