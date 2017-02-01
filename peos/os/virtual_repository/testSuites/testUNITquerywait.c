/************************************************************************
 * Senior Design Project - PEOS Virtual Repository			*
 * Author : TASK4ONE							*
 * Filename : testUNITquerywait.c					*
 ************************************************************************/

/************************************************************************
 * Description:	Test the unit implementation of query_wait		*
 ************************************************************************/

#include "form.h"
#include "debug.h"
#include "variables.h"
#include "vrepo.h"
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h>
#include <stdbool.h>
#include <unistd.h>

#define BUFFER_SIZE 1000

int main( void )
{	
	void setInvalidResult( int, FILE * ) ;
	void setEmptyResult( int, FILE * ) ;
	void setExpectedResult ( char *, FILE * )  ;
	void setTestData ( char *, FILE * ) ;
	void callback( int size, resultList *listPointer , void *data ) ;
	void ( *call )( int, resultList *, void * data ) ;
	
	char queryString[BUFFER_SIZE] = { '\0' } ;
	char tempString[BUFFER_SIZE] = { '\0' } ;
	char *testString;
	int *d, index,  numQueries;
	queryList *tempQueries ;
	FILE *expectedResultFile, *testInputInvalid, *testInputEmpty, *testInputValid ;	
	
	//set expectedResultInvalidFile
	
	testInputInvalid = fopen ( "UNITquerywaitInvalid.dat", "r" ) ;
	_assert( __FILE__, __LINE__, testInputInvalid ) ;
	numQueries = 0;
	while ( !feof( testInputInvalid ) ) 
	{
		fgets ( queryString, sizeof ( queryString ), testInputInvalid ) ;
		if( strlen( queryString ) )
		{
			query_wait( queryString, call, d ) ;
			queryString[0] = '\0' ;
			numQueries++;			
		}
	}
	fclose( testInputInvalid ) ;

	expectedResultFile = fopen ( "UNITquerywaitExpectedResult.txt", "w" ) ;
	_assert( __FILE__, __LINE__, expectedResultFile ) ;
	setInvalidResult( numQueries, expectedResultFile ) ;
	
	printQueryList(myQueries);
	fwrite( "\nqueue list is empty!\n\n", sizeof( char ), strlen("\nqueue list is empty!\n\n"), expectedResultFile ) ;
	
	testInputEmpty = fopen ( "UNITquerywaitEmpty.dat", "r" ) ;
	_assert( __FILE__, __LINE__, testInputEmpty ) ;
	numQueries = 0;
	while ( !feof( testInputEmpty ) ) 
	{
		fgets ( queryString, sizeof ( queryString ), testInputEmpty ) ;
		if( strlen( queryString ) )
		{
			query_wait( queryString, call, d ) ;
			queryString[0] = '\0' ;
			numQueries++;			
		}
	}
	fclose( testInputEmpty ) ;
	setEmptyResult( numQueries, expectedResultFile ) ;
	
	printQueryList(myQueries);
	fwrite( "\nqueue list is empty!\n\n\n", sizeof( char ), strlen("\nqueue list is empty!\n\n\n"), expectedResultFile ) ;	
	
	testInputValid = fopen ( "UNITquerywaitValid.dat", "r" ) ;
	_assert( __FILE__, __LINE__, testInputValid) ;
	numQueries = 0;
	while ( !feof( testInputValid ) ) 
	{
		fgets ( queryString, sizeof ( queryString ), testInputValid ) ;
		if( strlen( queryString ) )
		{
			strcpy(tempString,queryString);
			query_wait( queryString, call, d ) ;
			fwrite( "query is ", sizeof( char ), strlen("query is "), expectedResultFile ) ;
			fwrite( tempString, sizeof ( char ), strlen( tempString ), expectedResultFile ) ;
			queryString[0] = '\0' ;
			numQueries++;
		}
	}
	fclose( testInputValid ) ;
	
	printQueryList(myQueries);
	fclose( expectedResultFile ) ;
	
	return 0 ;
}


void setInvalidResult( int invalids, FILE *expectedResultInvalidFile )
{
	int i ;
	char invalidString[] = "invalid query...\n" ;
	
	for( i = 0 ; i < invalids ; i++ )
		fwrite( invalidString, sizeof( char ), strlen( invalidString ), expectedResultInvalidFile ) ;
}

void setEmptyResult( int invalids, FILE *expectedResultInvalidFile )
{
	int i ;
	char invalidString[] = "empty query...\n" ;
	
	for( i = 0 ; i < invalids ; i++ )
		fwrite( invalidString, sizeof( char ), strlen( invalidString ), expectedResultInvalidFile ) ;
}


void callback( int size, resultList *listpointer, void *data )
{	
		
}

