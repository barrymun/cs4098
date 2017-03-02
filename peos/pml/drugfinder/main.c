# include <stdio.h>
# include <errno.h>
# include <stdlib.h>
# include <string.h>
# include <unistd.h>
# include <pml/parser.h>
# include <pml/scanner.h>
# include "global.h"
# include "local.h"
# include "common.h"
FILE *out ;
extern int main (
# ifdef ANSI_PROTOTYPES
    int			/* argc */,
    String *		/* argv */
# endif
);
void GetDrugList(Tree tree) 
{	
out=fopen("drug_list.txt", "ab");
  if(IS_OP_TREE(tree)) {
	if(HasAttribute(tree->left)){
		if(strcmp(GetAttributeName(tree->left),"list")==0){
		  fprintf(out,"%s\n",TREE_ID(tree->right));
		}
	}	
	else{
		GetDrugList(tree->left);
		GetDrugList(tree->right);
	}
  }
}

int main (argc, argv)
     int     argc;
     String *argv;
{
     out= fopen("drug_list.txt", "w+");
	if (out == NULL)
	{
	    printf("Error opening file!\n");
	    exit(1);
	}
  int index=0;
  filename = "-";
   Node node;
  do {
    if (optind < argc) {
      filename = argv [optind];
      lineno = 1;
    }
    
  if ((yyin = fopen (filename, "r")) != NULL) {
	      if (yyparse ( ) == 0) {
			ReduceGraph (program);
		for (node = program -> source; node != NULL; node = node -> next){
		      if (node -> requires != NULL){
				GetDrugList (node -> requires);
				index=index+1;
			}
		}
		GraphDestroy (program);
	    }else{
	    }
	      fclose (yyin);
    } else {
      fprintf (stderr, "%s: ", argv [0]);
      perror (filename);
    }
    
  } while (++ optind < argc);
	
	
  return 0;
}


