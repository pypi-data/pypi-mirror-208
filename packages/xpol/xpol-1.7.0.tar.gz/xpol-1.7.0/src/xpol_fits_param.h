#include <stdlib.h>
#include <stdio.h>

#ifndef XPOL_PARREADER
#define XPOL_PARREADER

#define _PAR_TRUE 1
#define _PAR_FALSE 0




/*
 * parcontent : structure containing the read parameter file
 */
 
typedef struct {
  
  /* ---- Parameter nside ----------------------------------------------
   *  Define nSide of Maps
   */
  int nside;
  
  /* ---- Parameter nstokes --------------------------------------------
   *  Define number of stokes parameters
   */
  int nstokes;
  
  /* ---- Parameter nmaps --------------------------------------------
   *  Define number of maps
   */
  int nmaps; 

  /* ---- Optional Parameter lmax --------------------------------------
   *  Define maximum multipole
   */
  int lmax;
  int flag_lmax;  /* ==_PAR_TRUE if lmax is present */

  /* ---- Optional InputList map --------------------------------------
   *  MAP FITS file
   */
  int flag_mapfile;
  char **mapfile;
  long n_mapfile; /* ==number_of_map */

  /* ---- Optional InputList bell --------------------------------------
   *  Beam window function
   */
  char **bell;
  int flag_bell;  /* ==_PAR_TRUE if bell is present */
  long n_bell; /* ==number_of_bell */
  
  /* ---- Optional InputList fell --------------------------------------
   *  Filter transfer function
   */
  char **fell;
  int flag_fell;  /* ==_PAR_TRUE if fell is present */
  long n_fell; /* ==number_of_fell */
  
  /* ---- Optional InputList weightI -----------------------------------
   *  WEIGHT for temperature
   */
  char **weightI;
  int flag_weightI;  /* ==_PAR_TRUE if weightI is present */
  long n_weightI; /* ==number_of_weightI */
  
  /* ---- Optional InputList weightP -----------------------------------
   *  WEIGHT for polarization
   */
  char **weightP;
  int flag_weightP;  /* ==_PAR_TRUE if weightP is present */
  long n_weightP; /* ==number_of_weightP */
  
  /* ---- Optional InputList noise_spectrum ----------------------------
   *  Noise power spectrum
   */
  char **noise_spectrum;
  int flag_noise_spectrum;  /* ==_PAR_TRUE if noise_spectrum is present */
  long n_noise_spectrum; /* ==number_of_noise_spectrum */
  
  /* ---- Optional Parameter SimuSpectra -------------------------------
   *  FITS file spectra for simulations
   */
  char *SimuSpectra;
  int flag_SimuSpectra;  /* ==_PAR_TRUE if SimuSpectra is present */
  
  /* ---- Optional Parameter SimuSeed ----------------------------------
   *  Seed for map generation
   */
  int SimuSeed;
  int flag_SimuSeed;  /* ==_PAR_TRUE if SimuSeed is present */
  
  /* ---- Optional InputList bell --------------------------------------
   *  Beam window function
   */
  char **SimuBell;
  int flag_SimuBell;  /* ==_PAR_TRUE if bell is present */
  long n_SimuBell;    /* ==number_of_bell */
  
  /* ---- Optional InputList Noise -----------------------------------
   *  NOISE for simulations
   */
  double *SimuNoise;
  int flag_SimuNoise;  /* ==_PAR_TRUE if SimuNoise is present */
  long n_SimuNoise;    /* ==number_of_SimuNoise */
  
  /* ---- Optional InputList SimuMapNoise ----------------------------------
   *  NOISE MAP for simulations
   */
  char **SimuMapNoise;
  int flag_SimuMapNoise;  /* ==_PAR_TRUE if SimuMapNoise is present */
  long n_SimuMapNoise;    /* ==number_of_SimuMapNoise */
  
  /* ---- Optional InputList SimuNhit ----------------------------------
   *  NHIT for inhomogeneous simulations
   */
  char **SimuNhit;
  int flag_SimuNhit;  /* ==_PAR_TRUE if SimuNhit is present */
  long n_SimuNhit;    /* ==number_of_SimuNhit */
  
  /* ---- Optional InputList SimuMapVariance ----------------------------------
   *  Noise Variance map for simulations
   */
  char **SimuMapVariance;
  int flag_SimuMapVariance;  /* ==_PAR_TRUE if SimuMapVariance is present */
  long n_SimuMapVariance;    /* ==number_of_SimuMapVariance */
  
  /* ---- Optional Input mllinfile --------------------------------
   *  Mll FITS input file
   */
  char *mllinfile;
  int flag_mllinfile;  /* ==_PAR_TRUE if mllinfile is present */

  /* ---- Optional Input mlloutfile ------------------------------------
   *  Mll output file
   */
  char *mlloutfile;
  int flag_mlloutfile;  /* ==_PAR_TRUE if mlloutfile is present */
  
  /* ---- Optional Input bintabTT --------------------------------------
   *  Binning for temperature spectrum
   */
  char *bintabTT;
  int flag_bintabTT;  /* ==_PAR_TRUE if bintabTT is present */
  
  /* ---- Optional Input bintabTP --------------------------------------
   *  Binning for temperature-polarization TE and TB spectra
   */
  char *bintabTP;
  int flag_bintabTP;  /* ==_PAR_TRUE if bintabTP is present */
  
  /* ---- Optional Input bintabPP --------------------------------------
   *  Binning for polarization EE, BB and EB spectra
   */
  char *bintabPP;
  int flag_bintabPP;  /* ==_PAR_TRUE if bintabPP is present */
  
  /* ---- Optional Output cross --------------------------------------
   *  Spectrum object name
   */
  char *cross;
  int flag_cross;  /* ==_PAR_TRUE if cell is present */
  
  /* ---- Optional Output cell --------------------------------------
   *  Spectrum object name
   */
  char *cell;
  int flag_cell;  /* ==_PAR_TRUE if cell is present */
  
  /* ---- Optional Output pseudo ------------------------------------
   *  Spectrum object name
   */
  char *pseudo;
  int flag_pseudo;  /* ==_PAR_TRUE if pseudo is present */

  /* ---- Parameter icross (xpol_fisher) ------------------------------------
   *  icross1 and icross2
   */
  int flag_icross1, flag_icross2;
  int icross1, icross2;

  /* ---- Optional Parameter remove_dipole ------------------------------------
   *  Calib factor
   */
  int *remove_dipole;
  int flag_remove_dipole;  /* ==_PAR_TRUE if remove_dipole is present */
  long n_remove_dipole; /* ==number_of_remove_dipole */
  
  /* ---- Optional Output kllfile ------------------------------------
   *  Covariance matrice object name
   */
  char *kll;
  int flag_kll;

  char *kl;
  int flag_kl;

  char *inv_kll;
  int flag_inv_kll;

  int tag_kll;
  int flag_tag_kll;
  
  /* ---- Optional Output WindowFunction ------------------------------------
   *  Window Function object name
   */
  char *WindowFunction;
  int flag_WindowFunction;
  
  /* ---- Optional Parameter no_error -----------------------------------
   *  Avoid computing error bars [default=0]
   */
  int no_error;
  int flag_no_error;
  
  /* ---- Optional Parameter verbose -----------------------------------
   *  Verbosity level. 0 : normal, 1:verbose
   */
  int ll2pi;
  int flag_ll2pi;
  
  /* ---- Optional Parameter verbose -----------------------------------
   *  Verbosity level. 0 : normal, 1:verbose
   */
  int verbose;
  int flag_verbose;


} parContent;



parContent* init_parContent( char *pioParFileName, FILE *logger);
void free_parContent( parContent **self);


#endif

