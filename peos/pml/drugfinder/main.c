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

extern int main (
# ifdef ANSI_PROTOTYPES
    int			/* argc */,
    String *		/* argv */
# endif
);
static void GetDrugList(tree, node, graph) 
	 Tree  tree;
     Node  node;
     Graph graph;
{
	FILE *out = fopen("drug_list.txt", "w+");
	if (out == NULL)
	{
	    printf("Error opening file!\n");
	    exit(1);
	}

  if(IS_OP_TREE(tree)) {
	if(HasAttribute(tree->left)){
		if(strcmp(GetAttributeName(tree->left),"list")==0){
			fprintf(out,"%s",TREE_ID(tree->right));	
		}
	}	
	else{
		GetDrugList(tree->left,node,graph);
		GetDrugList(tree->right,node,graph);
	}
  }
}

int main (argc, argv)
     int     argc;
     String *argv;
{
  
  int status;
  filename = "-";
  status = EXIT_SUCCESS;
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
				GetDrugList (node -> requires, node, program);
			}
		}

				GraphDestroy (program);
	    }else{
		status = EXIT_FAILURE;
	    }
	      fclose (yyin);
    } else {
      fprintf (stderr, "%s: ", argv [0]);
      perror (filename);
      status = EXIT_FAILURE;
    }
    
  } while (++ optind < argc);
  
  return 0;
}


