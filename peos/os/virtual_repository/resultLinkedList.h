/************************************************************************
 * Senior Design Project - PEOS Virtual Repository			*
 * Author : TASK4ONE							*
 * Filename : resultLinkedList.h					*
 ************************************************************************/

/************************************************************************
 * Description:	Contains function declarations for resultLinkedList.c	*
 ************************************************************************/

void printResultList( resultList *listpointer ) ;
void clearResultList( resultList *listpointer ) ;
resultList *removeResultItem( resultList *listpointer ) ;
resultList *addResultItem( resultList *listpointer , const char *data ) ;
