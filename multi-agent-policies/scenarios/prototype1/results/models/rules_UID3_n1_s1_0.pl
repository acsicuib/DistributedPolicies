
        :- use_module(library(lists)).
           route(xxxxxx, path(xxxx, xxx, []), 10, 10).
        nop(Si) :- serviceInstance(Si, S, N),
           service(S, HwReqs, MaxReqs, MaxLatency),
           node(N, Hw, Neighbours),
           findall(route(Si, P, PathLatency, UReqs), route(Si, P, PathLatency, UReqs), Routes),
           checkLatencies(Routes, MaxLatency, SumReqs),
           SumReqs =< MaxReqs.

fusion(Si1,Si2):- serviceInstance(Si1, S, N),
                serviceInstance(Si2, S, N),
                Si1 \== Si2,
                service(S, HwReqs, MaxReqs, MaxLatency),
                node(N, Hw, Neighbours),
                route(Si1,path(_, N1, NodesPath1), PathLatency1,UReqs1),
                route(Si2,path(_, N2, NodesPath2), PathLatency2,UReqs2),
                UReqs1 + UReqs2 < MaxReqs.

migrate(Si,TargetNode,MaxLatency):-
                serviceInstance(Si, S, N),
				service(S, HwReqs, MaxReqs, MaxLatency),
                node(N, Hw, Neighbours),
                node(TargetNode,HwTarget,_),
                member(TargetNode,Neighbours),
                link(N,TargetNode,L,B),
                route(Si,path(_, N, NodesPath), PathLatency,_),
                member(TargetNode,NodesPath),
                L > MaxLatency.

replicate(Si,TargetNodes):- serviceInstance(Si, S, N),
				service(S, HwReqs, MaxReqs, MaxLatency),
                node(N, Hw, Neighbours),
                selectTargets(Neighbours,TargetNodes).

replicate(Si,[N]):- serviceInstance(Si, S, N),
                service(S, HwReqs, MaxReqs, MaxLatency),
                node(N, Hw, Neighbours),
                route(Si,path(_, N, NodesPath), PathLatency,UReqs),
                UReqs > MaxReqs.

suicide(Si) :- serviceInstance(Si, S, N),
               service(S, HwReqs, MaxReqs, MaxLatency),
               findall(route(Si, P, PathLatency, UReqs), route(Si, P, PathLatency, UReqs), Routes),
               length(Routes,L),
               L is 0.

selectTargets([],[]).
selectTargets([N|Ns],[N|Ts]):-selectTargets(Ns,Ts).

checkLatencies([],_,0).
checkLatencies([route(Si, P, PathLatency, UReqs)|Ps], MaxLatency, SumReqs) :-
                            PathLatency =< MaxLatency,
                            checkLatencies(Ps, MaxLatency, SumReqsOld),
                            SumReqs is SumReqsOld + UReqs.

priority([replicate,nop,migrate,suicide]).
service(1,1,200,50).
serviceInstance(1,1,1).
node(1,4,[3, 2]).
node(3,6,[1, 4, 0]).
node(2,1,[1]).
link(1,3,20,1).
link(1,2,10,1).
route(1,path(0,1,[0, 3, 1]),45,14).
route(1,path(4,1,[4, 3, 1]),45,12).

query(nop(1)).
query(migrate(1, X, 1)).
query(replicate(1, X)).
query(suicide(1)).
query(fusion(X, Y)).
query(priority(X)).

        
        