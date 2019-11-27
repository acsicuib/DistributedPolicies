:- use_module(library(lists)).

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

priority([nop,migrate,replicate,suicide]).

service(meteo, 1, 200, 50).

serviceInstance(s42, meteo, n1).
serviceInstance(s45, meteo, n1).
serviceInstance(s43, meteo, n2).



node(n1, 3, [n3, n2]). %node(identifier, HW-capacity,neigh)
node(n2, 1, [n1]).
node(n3, 5, [n1, n4, n5]).
node(n4, 3, [n3]).
node(n5, 2, [n3]).


link(n1,n3,40,5). % link(source node, target node, latency, bw) 
link(n1,n2,10,5).

0.5::route(s42, path(n4, n1, [n4, n3, n1]), 45, 100); % route(S, Path, Latency, ReqsNo)
0.4::route(s42, path(n4, n1, [n4, n3, n1]), 45, 10). % route(S, Path, Latency, ReqsNo)

route(s45, path(n4, n1, [n4, n3, n1]), 45, 20).
0.20::route(s42, path(n5, n1, [n5, n3, n1]), 45, 20).
%0.80::route(s42, path(n5, n1, [n5, n3, n1]), 45, 0).


query(nop(s42)).
query(nop(s43)).
query(migrate(s42,X,1)).
query(replicate(s42,X)).
query(suicide(s42)).
query(suicide(s43)).
query(fusion(X,Y)).
query(priority(X)).

%writenl(priority([nop,migrate,replicate,suicide])).
