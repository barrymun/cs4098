#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#ifndef PALM
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <assert.h>
#include <time.h>
#endif
#include "error.h"
#include "process.h"
#include "events.h"
#include "graph.h"
#include "graph_engine.h"
#include "peos_util.h"

/* Globals. */


/* Forward declarations. */
extern peos_context_t *find_free_entry();

char *act_state_name(vm_act_state state) 
{
    switch (state) {
      case ACT_READY:
  	    return "READY";
	    break;
      case ACT_RUN:
  	    return "RUN";
	    break;
      case ACT_DONE:
  	    return "DONE";
	    break;
      case ACT_SUSPEND:
	    return "SUSPEND";
	    break;
      case ACT_NONE:
	    return "NONE";
	    break;
      case ACT_BLOCKED:
            return "BLOCKED";
            break;
      case ACT_PENDING:
	    return "PENDING";
	    break;
      case ACT_AVAILABLE:
	    return "AVAILABLE";
	    break;
      case ACT_SATISFIED:
	    return "SATISFIED";
	    break;
      default:
	    return "unknown syscall";
	    break;
      }
}

int peos_create_instance(char *model_file,peos_resource_t *resources,int num_resources)
{
    peos_context_t *context;

    if ((context = find_free_entry()) == NULL) {
	peos_error("peos_create_instance: no free entry in process table");
        return -1;
    }

    if ((context->process_graph = makegraph(model_file)) != NULL) {
	context->pid = peos_get_pid(context);
	context->num_resources = num_resources;
	context -> resources = resources;
        strcpy(context->model, model_file);
        context->status = PEOS_READY;
	initialize_graph(context->process_graph, context->pid);
	return (context->pid); 
    }
    peos_error("peos_create_instance: makegraph(%s) failed", model_file);
    return -1;
}

#ifndef PALM
void log_event(char *message)
{
    FILE *file;
    struct tm *current_info;
    time_t current;
    char times[50];
    int filedes;
    
    time(&current);
    current_info = localtime(&current);
    current = mktime(current_info);
    strftime(times,25,"%b %d %Y %H:%M",localtime(&current));

    filedes = open("event.log", O_RDWR | O_CREAT, S_IRUSR | S_IWUSR);
    if (filedes < 0) {
        peos_error("cannot get event log file descriptor\n");
	peos_perror("log_event");
	exit(EXIT_FAILURE);
    }
    
    if(get_lock(filedes) < 0) {
        peos_error("cannot obtain event log file lock\n");
	peos_perror("log_event");
	exit(EXIT_FAILURE);
    }
    
    file = fdopen(filedes, "a");

    fprintf(file, "%s %s\n", times,message);
    release_lock(filedes);
    fclose(file);
    close(filedes);
}
#endif	    



#ifdef UNIT_TEST
#include "test_process.c"
#endif
