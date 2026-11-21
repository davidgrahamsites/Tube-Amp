*-----------------------------------------------------------------------
* Filename:		12AX7s.inc  V1  3/9/97
* Simulator:		SPICE 3f4
* Device type:		Triode
* Device model:		12AX7/ECC83
*
* Author:		Duncan Munro
* Date:			3/9/97
* Copyright:		(C)1997-2000 Duncan Amplification
*
* Based on the 12AX7 model developed by Francesco Piazza, with
* the addition of behaviour at low anode voltages, and grid
* current.
*
* The following parameters are not modelled:
*
*   (1) Filament: A "cathode" connection is made which
*       should be connected to a potential which is the
*	average of the two filament terminals.
*
* Please note that this model is provided "as is" and
* no warranty is provided in respect of its suitability
* for any application.
*
* This model is provided for educational and non-profit use.
*
* Email queries to postmaster@duncanamps.com
*
* Pins   A  Anode
*        G  Grid
*        K  Cathode
*
*-----------------------------------------------------------------------
.SUBCKT 12AX7A A G K
*
* Calculate contribution to anode current
*
Bca	ca  0	V=45+V(A,K)+95.43*V(G,K)
*
* Reduction at low va
*
Bre	re  0	V=URAMP(V(A,K)/5)-URAMP(V(A,K)/5-1)
Baa	A   K	I=V(re)*1.147E-6*(URAMP(V(ca))^1.5)
*
* Grid current
*
Bgg	G   K	I=5E-6*(URAMP(V(G,K)+0.2)^1.5)
*
* Capacitances
*
Cgk G  K  1.6P
Cgp G  A  1.7P
Cpk A  K  0.46P
.ENDS 12AX7A
