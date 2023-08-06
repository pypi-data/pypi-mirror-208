#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

#include "mpi.h"
#include "s2hat.h"



#ifdef CNAG
  #include <nag.h>
  #include <nag_stdlib.h>
  #include <nagf07.h>
  #include <nagf06.h>
  #include <nagf16.h>
  #include <nagg05.h>
#endif

#ifdef MKL
  #include <mkl.h>
  #include "mkl_trans.h"
#endif

#ifdef ESSL
  #include <mkl.h>
  #include "mkl_trans.h"
#endif

#include "xpol_fits_param.h"


/* METHOD 0 = half cross */
/* METHOD 1 = 1x2 2x3 ... (n-1)xn nx1 */
/* METHOD 2 = all cross (n(n-1)/2 for pure modes but n*n for TE, TB and EB ) */
/* METHOD 3 = all cross but remove auto spectra even for TE, TB and EB ) PLANCK */
#define METHOD 3


//Table of contents
//-----------------
//    - Xpol maker
//    - format tools
//    - alms tools
//    - FITS tools
//    - Mll tools
//    - error bars

#ifndef UNDEF_HEALPIX_VALUE
#define UNDEF_HEALPIX_VALUE ( (const double)(-1.6375e30) )
#endif

#ifndef DBL_MAX
#define DBL_MAX            1.79769313486231470e+308
#endif

#ifndef MIN
#define MIN(x,y) (x<y ? x : y) /* Minimum of two arguments */
#endif
#ifndef MAX
#define MAX(x,y) (x>y ? x : y) /* Maximum of two arguments */
#endif
#ifndef SQR
#define SQR(a) ((a)*(a))
#endif

int fullsky;
int verbose;

#define HEAL_UNDEF(a) ( fabs(a-UNDEF_HEALPIX_VALUE) < 1e-5*fabs(UNDEF_HEALPIX_VALUE) )

#define OK 0
#define NOK 1

#define LEFT  10
#define RIGHT 11

FILE *logger;

/* for s2hat v00-02-01 */
/* #define s2hat_pixeltype pixeltype */
/* #define s2hat_scandef scandef */
/* #define s2hat_pixparameters pixparameters */
/* #define s2hat_int4 int4 */
/* #define s2hat_int8 int8 */
/* #define s2hat_flt8 flt8 */

#define Xread_vect read_fits_vect
#define Xread_map  read_fits_map
#define get_vect_size  get_fits_vect_size
#define EXIT_INFO(X,Y,Z,args...) { fprintf( X, "[%s:%d] "Z,__func__, __LINE__, ##args); fflush(X); MPI_Abort( MPI_COMM_WORLD, Y); exit(Y); }
#define INFO(X,Y,args...)        { fprintf( X, Y, ##args); fflush(X); }


//-----------------------------------------------------------
// MLL
//-----------------------------------------------------------
typedef struct {
  int nstokes;
  int ntt, ntp, npp;
  double *tttt, *eeee, *eebb, *tete, *etet, *ebeb;
  int is2;
  double *tttt2, *eeee2, *eebb2;
} XMll;





//-----------------------------------------------------------
// XMat
//-----------------------------------------------------------
typedef struct {
  int nstokes;

  int lmax, ntt, ntp, npp;
  double *tt, *tp, *pp;

} XMat;


//-----------------------------------------------------------
// XBin
//-----------------------------------------------------------
typedef struct {
  int nstokes;
  int lmax, ntt, ntp, npp;
  int *tt, *tp, *pp;

} XBin;


//-----------------------------------------------------------
// XPowSpec
//-----------------------------------------------------------
typedef struct {
  int nstokes;
  int ntt, npp, ntp;
  double *tt, *gg, *cc, *tg, *gt, *tc, *ct, *gc, *cg;
  double *ltt, *lpp, *ltp;
  double *tt2, *gg2, *cc2;
  int is2, isl;
} XPowSpec;


  






s2hat_int4 compute_all_xls( s2hat_int4 nmaps, s2hat_int4 noStokes, s2hat_int4 nlmax, s2hat_int4 nmvals, s2hat_int4 *mvals, s2hat_int4 lda,
			    s2hat_dcomplex *local_alm, s2hat_int4 nxtype, s2hat_flt8 *xcl, s2hat_int4 *frstSpec, s2hat_int4 *scndSpec, s2hat_int4 gangSize, 
			    s2hat_int4 n_gangs, s2hat_int4 my_gang_no, s2hat_int4 my_gang_rank, s2hat_int4 gang_root, MPI_Comm my_gang_comm, MPI_Comm global_comm);

s2hat_int4 compute_all_xls_numbers( s2hat_int4 nmaps, s2hat_int4 *frstSpec, s2hat_int4 *scndSpec, s2hat_int4 gangSize, s2hat_int4 n_gangs, s2hat_int4 my_gang_no, 
				    s2hat_int4 my_gang_rank, s2hat_int4 gang_root);


/* int4 compute_all_xls( int4 nmaps, int4 noStokes, int4 nlmax, int4 nmvals, int4 *mvals, int4 lda, */
/* 		      s2hat_dcomplex *local_alm,  */
/* 		      int4 nxtype, flt8 *xcl, int4 *frstSpec, int4 *scndSpec, */
/* 		      int4 gangSize, int4 n_gangs, int4 my_gang_no, int4 my_gang_rank, int4 gang_root, MPI_Comm my_gang_comm, MPI_Comm global_comm); */

/* int4 compute_all_xls_numbers( int4 nmaps, int4 *frstSpec, int4 *scndSpec, */
/* 			      int4 gangSize, int4 n_gangs, int4 my_gang_no, int4 my_gang_rank, int4 gang_root); */





//=========================================================================
//Mll tools (xpol_mll)
//=========================================================================
void CorrectMll( int local_lmin, int local_lmax, int nside,
		 double *bell1, double *bell2, double *fell,
		 XMll mll, XMll *mbb, int root, MPI_Comm comm);
void mll_pol( int lmin, int lmax, int nlmax, double *well, XMll *mll);

void wig3j_( double *L2, double *L3, double *M2, double *M3,
	     double *L1MIN, double *L1MAX, double *THRCOF, int *NDIM, int *IER);
void wig3j_c( int l2, int l3, int m2, int m3, double *wigner);

void XMll_alloc( XMll *mll, int ns, int nell1, int nell2, int nell3);
void XMll_alloc2( XMll *mll);
void XMll_dealloc( XMll *mll);
void XMll_dealloc2( XMll *mll);
void XMll_diagonal( XMll mll);
void XMll_SetToZero( XMll mll);
void XMll_SwapTE( XMll *M);
void XMll_Invert( XMll *M);
void XMll_pixwin( int nside, XMll mll, int leftright);
void XMll_beam( XMll mll, double *bellA, double *bellB);
void XMll_beam_sym( XMll mll, double *bellA, double *bellB);
void XMll_copy( XMll mll, XMll *mllcpy);




//=========================================================================
//General tools (xpol_tools)
//=========================================================================
int Fblock( int nblock, int ntt, int ntp, int npp, int block1, int block2, int b1, int b2);
double get_sky_fraction( long nele, double *poids);
void make_pq( int ll2pi, XBin bintab, XMat *matp, XMat *matq);
void add_ell( XBin bintab, XPowSpec *spec);
void BinCreate( int lmax, int ns, int ntt, int ntp, int npp,
		double *bintt, double *bintp, double *binpp,
		XBin *bintab);
void apply_pixwin( int nside, int lmax, double *bell);

void PCl_pol( XMat matp, XPowSpec pseudocl, XPowSpec *pseudocb);
void PMQ_pol( XMat matp, XMat matq, XMll mll, XMll *mbb);
void PMQ_pol2( int lmin, int lmax, XMat P, XMat Q, XMll mll, XMll *mbb);
void Xsolve( XMll M, XPowSpec *spec1, XPowSpec *spec2);
void remove_dipole( int flag, s2hat_pixeltype cpixelization, int first_ring, int last_ring, int nside, int map_size,
		    double *map, double *weight, int gangnum, int rank, int root, MPI_Comm comm);
long s2hat_globalpix( s2hat_pixeltype cpixelization, int first_ring, int last_ring, int nside, long local_pix);

void init_internal_random( int seed, int myid, int root, MPI_Comm comm);
void internal_gaussran( long nombre, double *nombre_hasard, int nprocs, int rank, int root, MPI_Comm comm);
void add_gaussran( long nombre, double *local_noise, int nprocs, int rank, int root, MPI_Comm comm);
void get_random_alms( int lmax, double *cl, int noStokes, int nmvals, int *mvals, s2hat_dcomplex *alms, int nprocs, int rank, int root, MPI_Comm comm);


//=========================================================================
//errorbars (xpol_tools)
//=========================================================================
void calcul_errorbar( XBin bintab, double fskyI, double fskyP,
		      XPowSpec crossAC, XPowSpec crossBD, XPowSpec crossAD, XPowSpec crossBC,
		      XPowSpec error);
void calcul_errorbar_full( XBin bintab, XMll invmll_AB, XMll mll_AA_BB, XMll mll_AB_BA,
			   XPowSpec crossAA, XPowSpec crossBB, XPowSpec crossAB, XPowSpec crossBA,
			   double *F, int root, MPI_Comm comm);


//=========================================================================
//MPI tools (xpol_tools)
//=========================================================================
int MPI_Mllreduce( XMll Msend, XMll *Mrecv, MPI_Datatype datatype, MPI_Op op, int root, MPI_Comm comm);
int MPI_Mllbcast( XMll M, MPI_Datatype datatype, int root, MPI_Comm comm);
int MPI_AllreducePowSpec( XPowSpec Sspec, XPowSpec *Rspec, MPI_Datatype datatype, MPI_Op op, MPI_Comm comm);
int MPI_BcastPowSpec( XPowSpec spec, MPI_Datatype datatype, int root, MPI_Comm comm);



//=========================================================================
//Struct
//=========================================================================
void XMat_alloc( XMat *mat, int ns, int ellmax, int nell1, int nell2, int nell3);
void XMat_dealloc( XMat *mat);

void XBin_alloc( XBin *bintab, int ns, int ellmax, int nell1, int nell2, int nell3);
void XBin_dealloc( XBin *bintab);
void XBin_read( int nstokes, int lmax, char* file_bintabTT, char* file_bintabTP, char* file_bintabPP, XBin *bintab);

void XPowSpec_alloc( XPowSpec *spec, int ns, int nell1, int nell2, int nell3);
void XPowSpec_alloc2( XPowSpec *spec);
void XPowSpec_allocl( XPowSpec *spec);
void XPowSpec_deallocl( XPowSpec *spec);
void XPowSpec_dealloc2( XPowSpec *spec);
void XPowSpec_dealloc( XPowSpec *spec);

double *XPow2Spec( int tag, XPowSpec cl);
double *XMll2Mat( int tag1, int tag2, XMll mll);
int XBin2NBin( int tag, XBin bintab);
int *XBin2Bintab( int tag, XBin bintab);



//=========================================================================
//Algebra
//=========================================================================
void PMQ( int nbin, int nele, double *P, double *V, double *Q, double *M);
void PMQlocal( int lmin, int lmax, int nbin, int nele, double *P, double *V, double *Q, double *M);
void PCl( int nele, int nbin, double *matp, double *pseudocl, double *pseudocb);
double SolveSystem( int nele, double *mat, double *cell);
void Xinvert( int nbin, double *mat);
void PM( int nbin, int nele, double *P, double *M, double *PM);
void MFM( int nbin, int nele, double *P, double *V, double *Q, double *M);



//=========================================================================
//Fits tools
//=========================================================================
int Xread_map( int nside, int ncol, char *infile, double *map);
int Xread_vect( char *infile, double *vect, int lmax, int colnum);
int get_vect_size( char *infile, int lmax);
void XBin_read( int nstokes, int lmax, char* file_bintabTT, char* file_bintabTP, char* file_bintabPP, XBin *bintab);


//=========================================================================
//Fits tools
//=========================================================================
int get_parameter(const char *fname, const char *nom, char *value, int prt);

void read_fits_spec( int nstokes, char *infile, XPowSpec *spec, XPowSpec *err, int is2);
void read_TQU_maps( int nside, double *map, char *infile, int nstokes);
void read_fits_mll( char *infile, XMll *mll);
void read_fits_mbb( char *infile, XMll *mll);
int read_fits_vect( char *infile, double *vect, int nele, int colnum);

void write_fits_map( int nstokes, int npix, double *map, char *outfile);
void write_fits_vect( int nele, double *vect, char *outfile, int hdu);
void write_fits_mll( XMll mll, char *outfile);
void write_fits_mbb( XMll mll, char *outfile);
void write_fits_pseudo( char *outfile, XPowSpec cell);
void write_fits_spec( char *outfile, XBin bintab, double fsky, XPowSpec cell, XPowSpec err);
void write_fits_spec_full( char *outfile, XBin bintab, XPowSpec cell, XPowSpec err, XPowSpec cosmic);

void collect_write_map( s2hat_pixeltype cpixelization, s2hat_int4 nmaps, s2hat_int4 mapnum, s2hat_int4 nstokes,
                        char *mapname, s2hat_int4 first_ring, s2hat_int4 last_ring, s2hat_int4 map_size,
                        s2hat_flt8 *local_map, s2hat_int4 myid, s2hat_int4 numprocs, s2hat_int4 root, MPI_Comm comm);

void read_and_distribute_map( s2hat_pixeltype cpixelization, s2hat_int4 nmaps, s2hat_int4 mapnum, s2hat_int4 nstokes, 
			      char *mapname, s2hat_int4 first_ring, s2hat_int4 last_ring, s2hat_int4 map_size, 
			      s2hat_flt8 *local_map, s2hat_int4 myid, s2hat_int4 numprocs, s2hat_int4 root, MPI_Comm comm);

void Xcreate_vect( char *filename, int nele, int ncols, char **colnames, char **coltype);
void Xwrite_vect( int nele, double *vect, char *filename, int col);






//=========================================================================
//Fisher tools (xpol_fisher_tools.c)
//=========================================================================
void Xcreate_list( int nbol, int **list);
void Xcreate_noautolist( int tag, int nbol, int **listnoauto);

void combine_cross( int nbin, int nbol, int tag, XPowSpec **allcell, double *F, double *cell);
void combine_cross_full( int nbin, int nbol, int tag, XPowSpec **allcell, double *F, double *cell);
void get_kll( int nbin, int nbol, double *F, double *kll, int tag);
void extract_err( int nstokes, XPowSpec kll, XPowSpec *err);
void Fish2Err( int nbintot, double *Fish, XPowSpec *err);
void prepare_xcorrelation( int nside, int lmax, int nstokes, int *eop, double *bell, 
			   char **weightI, char **weightP, XMat matp, XMat matq,
			   XMll *invmll_A_B, XMll *invmll_C_D, XMll *mll_AC_BD, XMll *mll_AD_BC, int root, MPI_Comm comm);
void xcorrelation( int tag, int ncross, int c1, int c2, XBin bintab, double fsky_t, double fsky_p,
		   XPowSpec specAC, XPowSpec specBD, XPowSpec specAD, XPowSpec specBC, 
		   XMll invmll_AB, XMll invmll_CD, XMll mll_AC_BD, XMll mll_AD_BC, double *corr, int root, MPI_Comm comm);
void compute_xcorr( int nbin, int *bintab,
		    double *specAC, double *specBD, double *specAD, double *specBC,
		    double fsky, double *corr);
void compute_pcl_variance( int nbin, int *bintab,
			   double *specAC, double *specBD, double *specAD, double *specBC,
			   double *mll_AC_BD, double *mll_AD_BC, 
			   double *corr, int root, MPI_Comm comm);
void mll_pcldiag_mll( int nblock, XMll invmll1, double *F, XMll invmll2);
void mll_pclcov_mll( int nblock, XMll invmll1, double *F, XMll invmll2);

void compute_cosmicvar( XBin bintab, XMll mll, double fsky_t, double fsky_p, XPowSpec cell, double *cosmic, int tag);
void compute_cosmic( XBin bintab, double fsky_t, double fsky_p, XPowSpec cell, double *cosmic, int tag);
void compute_cosmic_full( XBin bintab, double *mll, XPowSpec cell, double *cosmic, int tag);


void WindowFunc( int lmax, int nbin, double *matp, double *mll, double *mbb, double *wbl);
void WindowFuncPol( int lmax, int nbin, double *matp, double *mll_EEEE, double *mll_EEBB, double *mbb_EEEE, double *mbb_EEBB, 
		    double *wbl_EEEE, double *wbl_EEBB);

void compute_mll( int nside, int lmax, int nstokes, double *maskI, double *maskP, 
		  XMll *mbb, double *fsky, int root, MPI_Comm comm);












#define Fvalue(M, ncross, nbin, c1, c2, b1, b2) M[(long)(b1*ncross+c1)*(long)(nbin*ncross)+(long)(b2*ncross+c2)]




//-----------------------------------------------------------
// List
//-----------------------------------------------------------
#if METHOD == 0

#define NALL(nbol)   (nbol*(nbol+1)/2)
#define NCROSS(tag,nbol) (nbol*(nbol-1)/2)

#elif METHOD == 1

#define NALL(nbol)   (2*nbol)
#define NCROSS(tag,nbol) (nbol)

#elif METHOD == 2

#define NALL(nbol)    (nbol*nbol)
#define NCROSS(tag,nbol)  ( (tag<4 || tag>6) ? nbol*(nbol-1)/2 : nbol*nbol )

#elif METHOD == 3

#define NALL(nbol)    (nbol*nbol)
#define NCROSS(tag,nbol)  ( (tag<4 || tag>6) ? nbol*(nbol-1)/2 : nbol*(nbol-1) )

#endif


