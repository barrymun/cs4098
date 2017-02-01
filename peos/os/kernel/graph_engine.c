#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef PALM
#include <time.h>
#include "predicate_evaluator.h"
#include "resources.h"
#endif
#include "error.h"
#include "process.h"
#include "action.h"
#include "graph.h"
#include "pmlheaders.h"
#include "process_table.h"
#include "graph_engine.h"

void handle_selection(Node n);
int mark_successors(Node n, vm_act_state state);
void add_iteration_lists(Graph g);
int set_rendezvous_state(Node n);
vm_act_state set_node_state (Node n, vm_act_state state, int* error);
vm_exit_code set_act_state_graph(Graph g, char *action, vm_act_state state);

void sanitize(Graph g)
{
    Node n;
    for(n = g -> source; n != NULL; n = n -> next) {
	sanitize_node(n);
    }
}

/* 
 * Find Iteration begin and End Nodes. If the node is a beginning of an 
 * iteration, then the flag ITER_START is set to true. If the node is at the 
 * end of an iteration, then the flag ITER_END will be set to true. 
 * All the nodes in the node list are arranged in lexicographic order. 
 * We start with the first node after the source and mark it. If a node 
 * has its predecessor which is not marked, then the predecessor is 
 * the end of an iteration. Similarly, if the node has a successor 
 * which is marked, then the successor is the start of an iteration 
 *
 */

void mark_for_iteration(Graph g)
{
    Node node,parent,child;
    int i,k;

    MARKED_0(g -> source) = TRUE;
    for(node = g -> source->next; node != NULL; node = node -> next) {
        for(i = 0; i < ListSize(node -> predecessors); i++) {
            parent = (Node) ListIndex(node -> predecessors,i);
            if (MARKED_0(parent) == FALSE) {
	        ITER_START(node) = TRUE;
	    }
	}

	MARKED_0(node) = TRUE;
        for(k = 0; k < ListSize(node -> successors); k++) {
            child = (Node) ListIndex(node -> successors,k);
            if (MARKED_0(child) == TRUE) {
	        ITER_END(node) = TRUE;
	    }
	}
    }

}

/* 
 * At the beginning of an iteration, the first action(or a selection or a 
 * branch) in an iteration and the action following that iteration will be 
 * ready. When an iteration starts, we need to set the action 
 * (or selection or branch) following that iteration to ACT_NONE and 
 * vice versa. So there is a list of nodes associated with each action. 
 * The list ITER_END_NODES will be associated with a starting node of 
 * an iteration and it contains the list of nodes following the iteration 
 * for which this node is a start node.There can be more than one 
 * iterations with a given node as a start node and hence this list can 
 * have more than one node. Similarly, the list ITER_START_NODES is 
 * associated with contains the list of all nodes which are the 
 * starting nodes of the iterations with this node as the node following 
 * that iteration. And since more than one iteration can end at a given 
 * node, this is also a list of nodes rather than a single node. This function 
 * just makes these lists for each node.
 *
 */

void add_iteration_lists(Graph g)
{
    Node node,child,parent,child1,child2;
    int i,j,k,l;

    MARKED_1(g -> source) = TRUE;

    for(node = g -> source->next; node != NULL; node = node -> next) {
        for(i = 0; i < ListSize(node -> predecessors); i++) {
	    parent = (Node) ListIndex(node -> predecessors,i);
	    if (MARKED_1(parent) == FALSE) {
	        for(j=0; j < ListSize(parent -> successors); j++) {
		    child = (Node) ListIndex(parent->successors,j);
		    if ((strcmp(child->name,node->name) != 0) && (ORDER(child) > ORDER(parent)))
		    {
                         ListPut(ITER_END_NODES(node),child);
		    }
		}
	     }
	}
	MARKED_1(node) = TRUE;
        for(k = 0; k < ListSize(node -> successors); k++) {
            child1 = (Node) ListIndex(node -> successors,k);
	    if (MARKED_1(child1) == TRUE) {
	        for(l = 0; l < ListSize(node -> successors); l++) {
	            child2 = (Node) ListIndex(node -> successors,l);
		    if (MARKED_1(child2) == FALSE) {
		        ListPut(ITER_START_NODES(child2),child1);
		    }
	        }
	    }
	 }
    }
}

/* 
 * Every action node will also have a list of super nodes associated with it. 
 * These nodes are the control flow nodes (selection or branch) under whose 
 * influence the given action node falls. For example for the folowing 
 * PML program: 
 * selection s1 {
 *   selection s2 {
 *      action a {} -- super nodes : s1,s2
 *      action b {} -- super nodes : s1.s2
 *      }
 *   action c {}  -- super nodes: s1
 *   }
 * 
 * This function adds these lists.
 *
 */
				
void add_super_node_lists(Graph g)
{
    Node n;

    for(n = g -> source -> next; n != NULL; n = n -> next) {
        if ((n -> type == SELECTION) || (n -> type == BRANCH)) {
            Node slave;
	    for(slave = n -> next; slave != n -> matching; slave = slave -> next) {
	        if (slave -> type  == ACTION) {
		    ListPut(SUPER_NODES(slave),n);
		}
	    }
	}
    }
}

/*
 * When a action gets set to run, it has to be checked if that action is 
 * part of an iteration. If yes, then the nodes, following that 
 * iteration should be set to none. This function does that. Also we have 
 * to do this recursively, because there can be iterations within iterations.
 *
 */

void set_iter_none(Node n, Node original)
{
    Node iter_start_node,iter_end_node;
    int i;

    for(i = 0; i < ListSize(ITER_START_NODES(n)); i++) {
        iter_start_node = (Node) ListIndex(ITER_START_NODES(n),i);
        if ((iter_start_node->type == SELECTION) || (iter_start_node->type == BRANCH) ||(iter_start_node->type == ACTION)) {
	    if ((strcmp(iter_start_node -> name, original -> name) != 0) && (MARKED_2(iter_start_node) == FALSE)) {
	        MARKED_2(iter_start_node) = TRUE;
                mark_successors(iter_start_node,ACT_NONE);
                set_iter_none(iter_start_node,original);
	    }
        }
    }


    for(i = 0; i < ListSize(ITER_END_NODES(n)); i++) {
        iter_end_node = (Node) ListIndex(ITER_END_NODES(n),i);
	if ((iter_end_node->type == SELECTION) || (iter_end_node->type == BRANCH) ||(iter_end_node->type == ACTION)) {
	    if ((strcmp(iter_end_node -> name, original -> name) != 0) && (MARKED_2(iter_end_node) == FALSE)) {	     
	        MARKED_2(iter_end_node) = TRUE;
	        mark_successors(iter_end_node,ACT_NONE);
	        set_iter_none(iter_end_node,original);
	    }
	}
    }
	
}

/*
 * When a node is set to ready and that node is the start node of an iteration,
 * then all the nodes following that iteration should also be ready. The 
 * first part of this function does that. Also, when a node is set to ACT_RUN 
 * and the node is  a start node of an iteration, then all the nodes following 
 * that iteration are set to none. And if the node is the end of an iteration, 
 * then the start of that iteration is to be set to NONE. This is done by 
 * calling the set_iter_none(node,original) function. The original node is 
 * the same node when called for the first time. This to prevent that node 
 * from being set to ACT_NONE, since it can be a member of ITER_START_NODES 
 * and ITER_END_NODES lists of other nodes.  
 *
 */

void mark_iter_nodes(Node n)
{
    Node iter_end_node;
    int i;
    if ((STATE(n) == ACT_READY) || (STATE(n) == ACT_BLOCKED)){
        for(i = 0; i <  ListSize(ITER_END_NODES(n)); i++) {
            iter_end_node = (Node) ListIndex(ITER_END_NODES(n),i);
	    if ((iter_end_node->type == SELECTION) || (iter_end_node->type == BRANCH) ||(iter_end_node->type == ACTION)) {
	        mark_successors(iter_end_node,ACT_READY);
	    }
	}
    }
    else {
        if (STATE(n) == ACT_RUN)	{
	    set_iter_none(n,n);
	}
    }
}

/*
 * This function sets all the super nodes of an action node to RUN. Every 
 * time a node is set to ACT_RUN, iterations have to be handled. Hence the 
 * call to mark_iter_nodes(..) after setting the state to ACT_RUN.
 *
 */

int set_super_nodes_run(Node n)
{
    int error;
    Node super;
    int i;
    for(i = 0; i <  ListSize(SUPER_NODES(n)); i++) {
        super = (Node) ListIndex(SUPER_NODES(n),i);
        set_node_state(super, ACT_RUN, &error);
        if (error)
            return 0;
        set_node_state(super -> matching, ACT_RUN, &error);
        if (error)
            return 0;
        mark_iter_nodes(super);
    }
    return 1;
}

/* 
 * This function marks the state of a given action/construct to the specified 
 * state. If the given node is a control flow construct, then it recursively 
 * traverses the successors of that node until it finds an action node and 
 * sets it state  to the state passed as an argument. After setting the 
 * state to ACT_RUN mark_iter_nodes is called to handle iterations.
 *
 */

int mark_successors(Node n, vm_act_state state)
{
    int error;
    int i;
    Node child;
    if (n -> type == ACTION) {
        set_node_state(n, state, &error);
        if (error)
            return 0;
        mark_iter_nodes(n);
        return 1;
    }
    else if ((n -> type == BRANCH) || (n -> type == SELECTION) || (n -> type == JOIN)) {
        if ((n->type == BRANCH) || (n->type == SELECTION)) {
            set_node_state(n, state, &error);
            if (error)
                return 0;
            mark_iter_nodes(n);
            set_node_state(n -> matching, state, &error);
            if (error)
                return 0;
        }
        for(i = 0; i < ListSize(n -> successors); i++) {
            child = (Node) ListIndex(n -> successors, i);
            mark_successors(child,state);
        }
    }
    return 1;
}

/* 
 * 
 * This function is called after an action is done and the node following it 
 * is a join node. It sets the join and the selection to ACT_DONE and since
 * this join can be followed by another join (for selection within selection)
 * or a rendezvous (for selection within branch), it recursively calls itself
 * and then calls the function to set the state of the rendezvous.
 *
 */

int propogate_join_done(Node n, vm_act_state state_set)
{
    int error;
    int i;
    Node child;
    if (n -> type == JOIN) {
        set_node_state(n, state_set, &error);
        if (error)
            return 0;
        set_node_state(n -> matching, state_set, &error);
        if (error)
            return 0;
	for(i = 0; i < ListSize(n->successors); i++) {
	    child = (Node) ListIndex(n->successors,i);
	    propogate_join_done(child, state_set);
	    set_rendezvous_state(child);
	}
    }
    return 1;
}

/*
 * 
 * Same as propogate_join_done(..) except that the rendezvous will not be 
 * done before all the nodes in that branch are done.
 *
 */

int set_rendezvous_state(Node n)
{
    int error;
    int i;
    Node child,parent;
    int status = 1;
    if (n -> type == RENDEZVOUS) {
        for(i = 0; i < ListSize(n -> predecessors); i++) {
            parent = (Node) ListIndex(n -> predecessors,i);
            if (STATE(parent) != ACT_DONE) {
                status = 0;
            }
        }
        if (status == 1) {
            set_node_state(n, ACT_DONE, &error); //only raise error when Node type is ACTION
            set_node_state(n -> matching, ACT_DONE, &error);
            for(i = 0; i< ListSize(n -> successors); i++) {
                child = (Node) ListIndex(n -> successors,i);
                if (child -> type == JOIN) {
                    propogate_join_done(child, ACT_DONE);
                }
                mark_successors(child,ACT_READY);
                set_rendezvous_state(child);
            }
        }
    }
    return 1;
}

void set_process_state(Graph g)
{
    Node parent;
    int i;
    int status = 1;

    for(i = 0; i < ListSize(g -> sink -> predecessors); i++) {
        parent = (Node) ListIndex(g -> sink -> predecessors,i);
        if ((ListSize(parent -> successors) > 1) || (STATE(parent) != ACT_DONE))
	    status = 0;
    }
    
    if (status == 1) {
	STATE(g -> source) = ACT_DONE;
        STATE(g -> sink) =  ACT_DONE;	
    }
}

/*
 * At any point more than one node cannot be in ACT_RUN state
 * This function takes care of that by setting all other actions
 * which are in ACT_RUN state to ACT_SUSPEND
 *
 */

int make_other_run_suspend(Graph g, char *act_name)
{
    int error;
    Node n;
    for(n = g -> source; n != NULL; n = n -> next) {
        if (n->type == ACTION) {
	    if (STATE(n) == ACT_RUN) {
	        if (strcmp(n->name, act_name) != 0) {
                    set_node_state(n, ACT_SUSPEND, &error); //only raise error when state is set to ready and done
		}
	    }
	}
    }
    return 1;
}    

int action_run(Graph g, char *act_name)
{
    int error;
    Node n;
    n = find_node(g, act_name);
    if (n != NULL) {
        set_node_state(n, ACT_RUN, &error); //only raise error when state is set to ready and done
	make_other_run_suspend(g, act_name);
	mark_iter_nodes(n);  /* handle iterations */
	handle_selection(n); /* handle selections */
	set_super_nodes_run(n); /*set super nodes to run */
        sanitize(g); /* sanitize the markers used */
    } else {
	return -1;
    }
    return 1;
}

/* 
 * This function handles selections. When an action within a selection is set 
 * to ACT_RUN, then all the siblings have to be set to ACT_NONE. Also, there 
 * can be recursive selections. So this function has to be recursive.  
 *
 */

void handle_selection(Node n)
{
    int i,j;
    Node parent;
    Node child;
 
    if ((n -> predecessors == NULL) || (MARKED_3(n) == TRUE))
        return;
		                                                                         
    MARKED_3(n) = TRUE;
 
    for(i = 0; i < ListSize(n -> predecessors); i++) {
        parent = (Node) ListIndex(n -> predecessors,i);
        if ((parent -> type) == SELECTION) {
            for(j=0; j < ListSize(parent -> successors); j++) {
                child = (Node) ListIndex(parent -> successors,j);
                if (strcmp((child->name),n->name) != 0) {
                    mark_successors(child,ACT_NONE);
                }
	     }
	}
	if (ORDER(n) >  ORDER(parent))  
        handle_selection(parent);
    }
    return;
}

vm_exit_code action_done(Graph g, char *act_name)
{
    int error;
    Node n;
    Node child;
    int i,num_successors;
    vm_act_state state_set;

    if (action_run(g, act_name) == -1) return VM_INTERNAL_ERROR;
    n = find_node(g,act_name);
    if (n != NULL) {
        state_set = set_node_state(n, ACT_DONE, &error);
        if (error)
            return VM_INTERNAL_ERROR;
	num_successors = ListSize(n -> successors);
	for(i = 0; i < num_successors; i++) {
	    child = (Node) ListIndex(n -> successors, i);
	    /*
	     * (num_successors == 1) is a check to see that it is 
	     * not an iteration.
	     */
	    if (state_set == ACT_DONE) {
                if ((child -> type == JOIN) && (num_successors == 1)) {
	            propogate_join_done(child, state_set);
	        }
	    }
	    if (child -> type != RENDEZVOUS) {
		/* 
		 * if a child is not a rendezvous or a join, it has to 
		 * be a selection or branch or action, so mark it ready. If 
		 * its sink, that is handled again by set_process_state(..) 
		 */
	        mark_successors(child, ACT_READY);
	    }
	    else {
	        if (num_successors == 1)	
		set_rendezvous_state(child);
	    }
	}	    
	if (num_successors == 1)
	    set_process_state(g);
    }
    else {
        fprintf(stderr, "Error in action_done");
	return VM_INTERNAL_ERROR;
    }
    if (STATE(g->source) == ACT_DONE) {
        return VM_DONE;
    }
    else
        return VM_CONTINUE;
}

char *get_script_graph(Graph g, char *action_name)
{
    Node n;
    n = find_node(g,action_name);
    if (n == NULL) {
        fprintf(stderr,"\n Error : get_script action node not found\n");
        return NULL;
    }	
    else
        return(n -> script ? n -> script : "(no script)");
}

vm_act_state get_act_state_graph(int pid, char *act_name) 
{
    Node n;
    Graph g;
    peos_context_t *context = peos_get_context(pid);
    if (context != NULL) {
        g = context->process_graph;
        n = find_node(g, act_name);
	if (n != NULL) {
            return STATE(n);
	}
	else 
	    return -1;
    }
    else
        return -1;
}

void initialize_graph(Graph g, int pid)
{
    Node n;
    int i = 0;
        
    for(n = g -> source; n != NULL; n = n -> next) {
        n -> data = (void *) malloc (sizeof (struct data));
	sanitize_node(n);
	PID(n) = pid;
	STATE(n) = ACT_NONE;
        ORDER(n) = i;
        i++;
        ITER_START(n) = FALSE;
        ITER_END(n) = FALSE;
        ITER_START_NODES(n) = ListCreate();
        ITER_END_NODES(n) = ListCreate();
	SUPER_NODES(n) = ListCreate();
    }
    add_super_node_lists(g); /* add the node lists */
    mark_for_iteration(g); /* mark beginning and end of iterations */
    add_iteration_lists(g);  /* add the iteration lists */
    sanitize(g); /* sanitize markers */
    mark_successors(g->source->next,ACT_READY);
}

vm_exit_code handle_resource_event(int pid, char *action, vm_resource_event event)
{
    int error;
    Graph g;
    Node n;
    peos_context_t *context = peos_get_context(pid);
    
    g = context -> process_graph;
    if (g == NULL) {
        peos_error("handle_resource_event: process graph is null");
	return VM_INTERNAL_ERROR;
    }

    n = find_node(g,action);

    if (n == NULL) {
	return VM_INTERNAL_ERROR;
    } 

    if (event == REQUIRES_TRUE) {
	if (STATE(n) == ACT_BLOCKED) {
	    set_node_state(n, ACT_READY, &error);
	    if (error) {
		return VM_INTERNAL_ERROR;
	    }
	} else {
	    if ((STATE(n) != ACT_READY) && (STATE(n) != ACT_RUN) && (STATE(n) != ACT_PENDING) && (STATE(n) != ACT_SUSPEND) && (STATE(n) != ACT_DONE)) {
		set_node_state(n, ACT_AVAILABLE, &error); /* only raise error when state is set to ready and done */
	    }
	}
	return VM_CONTINUE;
    } else if (event == PROVIDES_TRUE) {
	if ((STATE(n) == ACT_PENDING)) {
	    set_node_state(n, ACT_DONE, &error);
	    if (error) {
		return VM_INTERNAL_ERROR;
	    }
	} else if ((STATE(n) != ACT_DONE) && (n -> provides != NULL)) {
	    set_node_state(n, ACT_SATISFIED, &error);
	    if (error) {
		return VM_INTERNAL_ERROR;
	    }
	}
	return VM_CONTINUE;
    } else {
	peos_error("handle_resource_event: unknown event %d", event);
	return VM_INTERNAL_ERROR;
    }

}

int is_requires_true(Node n) {
    int i;
    int num_resources = 0;
    peos_resource_t* resources;
    peos_resource_t* proc_resources;
    peos_context_t* context = peos_get_context(PID(n));
    resources = get_resource_list_action_requires(PID(n), n->name, &num_resources);
    if (context && context->num_resources > 0) {
        proc_resources = (peos_resource_t *) calloc(context->num_resources, sizeof(peos_resource_t));
        for (i = 0; i < context->num_resources; i++) {
            strcpy(proc_resources[i].name, context->resources[i].name);
            strcpy(proc_resources[i].value, context->resources[i].value);
        }
        eval_resource_list(&proc_resources, context->num_resources);
        fill_resource_list_value(proc_resources, context->num_resources, &resources, num_resources);
    }
    return eval_predicate(resources, num_resources, n->requires);
}

int is_provides_true(Node n) {
    int i;
    int num_resources = 0;
    peos_resource_t* resources;
    peos_resource_t* proc_resources;
    peos_context_t* context = peos_get_context(PID(n));
    resources = get_resource_list_action_provides(PID(n), n->name, &num_resources);
    if (context && context->num_resources > 0) {
        proc_resources = (peos_resource_t *) calloc(context->num_resources, sizeof(peos_resource_t));
       for (i = 0; i < context->num_resources; i++) {
            strcpy(proc_resources[i].name, context->resources[i].name);
         strcpy(proc_resources[i].value, context->resources[i].value);
       }
       eval_resource_list(&proc_resources, context->num_resources);
       fill_resource_list_value(proc_resources, context->num_resources, &resources, num_resources);
    }
    return eval_predicate(resources, num_resources, n->provides);
}

vm_act_state set_node_state(Node n, vm_act_state state, int* error)
{
    int result;
    vm_act_state state_set = state;
    *error = 0;

    if (n->type != ACTION) {
        STATE(n) = state_set;
        return state_set;
    }

    switch(state_set) {
        case ACT_READY:
            result = is_requires_true(n);
            if (result == -1) {
                *error = 1;
                return STATE(n);
            }
            if (!result)
                state_set = ACT_BLOCKED;
            break;
        case ACT_DONE:
            result = is_provides_true(n);
            if (result == -1) {
                *error = 1;
                return STATE(n);
            }
            if (!result)
                state_set = ACT_PENDING;
            break;
    }
    STATE(n) = state_set;
    return state_set;
}

/* this function was earlier called handle_resource_change */
vm_exit_code update_process_state(int pid) {
    Graph g;
    Node n;
    int result;

    peos_context_t *context = peos_get_context(pid);

    if (context == NULL) {
        peos_error("update_process_state: cannot get context for pid=%d", pid);
        return VM_INTERNAL_ERROR;
    }

    g = context -> process_graph;

    if (g == NULL) {
        peos_error("update_process_state: cannot get graph for pid=%d", pid);
        return VM_INTERNAL_ERROR;
    }

    for (n = g->source->next; n != NULL; n = n->next) {
        if (n->type == ACTION) {
            result = is_requires_true(n);
            if (result == -1)
                return VM_INTERNAL_ERROR;
            if (result) {
                if (handle_resource_event(pid, n->name, REQUIRES_TRUE) == VM_INTERNAL_ERROR) {
                    return VM_INTERNAL_ERROR;
                }
            }
            result = is_provides_true(n);
            if (result == -1)
                return VM_INTERNAL_ERROR;
            if (result) {
                if (handle_resource_event(pid, n->name, PROVIDES_TRUE) == VM_INTERNAL_ERROR) {
                    return VM_INTERNAL_ERROR;
                }
            }
        }
    }
    return VM_CONTINUE;
}

vm_exit_code handle_action_change(int pid, char *action, vm_act_state state)
{
    Graph g;
    char msg[256], *this_state;
    vm_exit_code exit_status;

    peos_context_t *context = peos_get_context(pid);

    this_state = act_state_name(state);
    sprintf(msg, "%s %s %s %d ",login_name, this_state, action, pid);
    log_event(msg);

    g = context -> process_graph;
    if (g == NULL) {
        peos_error("handle_resource_event: process graph is null");
        return VM_INTERNAL_ERROR;
    }

    if ((exit_status =  set_act_state_graph(g, action, state)) == VM_DONE) {
        sprintf(msg,"%s DONE %s %d",login_name, context->model, pid);
        log_event(msg);
        delete_entry(context->pid);
  	return exit_status;
    }
    
    if (exit_status == VM_INTERNAL_ERROR) {  
        return exit_status;
    }
                                                                
    return exit_status;
}

vm_exit_code set_act_state_graph(Graph g, char *action, vm_act_state state)
{
    int error;
    Node n;
    switch(state)
    {
        case ACT_DONE:
            return action_done(g,action);
        case ACT_READY:
            n = find_node(g,action);
            if (n!=NULL) {
                set_node_state(n, ACT_READY, &error);
                if (!error)
                    return VM_CONTINUE;
            }
            return VM_INTERNAL_ERROR;
        case ACT_RUN:
            if (action_run(g,action) >  0)
                return VM_CONTINUE;
            return VM_INTERNAL_ERROR;
        case ACT_NONE:
            n = find_node(g,action);
            if (n != NULL) {
                set_node_state(n, ACT_NONE, &error);
                if (!error)
                    return VM_CONTINUE;
            }
            return VM_INTERNAL_ERROR;
        case ACT_SUSPEND:
            n = find_node(g,action);
            if (n != NULL) {
                set_node_state(n, ACT_SUSPEND, &error);
                if (!error)
                    return VM_CONTINUE;
            }
            return VM_INTERNAL_ERROR;
        case ACT_ABORT:
            n = find_node(g,action);
            if (n != NULL) {
                if (STATE(n) == ACT_RUN) {
                    set_node_state(n, ACT_NONE, &error);
                    if (error)
                        return VM_INTERNAL_ERROR;
                    update_process_state(PID(n));
                }
                return VM_CONTINUE;
            }
            return VM_INTERNAL_ERROR;
        default :
            fprintf(stderr, "Error Changing Action : Invalid Action State\n");
            return -1;
    }
}
# ifdef UNIT_TEST
#include "test_graph_engine.c"
#endif
