# Comparaison REST vs JSON-RPC (TP 5 à 8)

1. REST (MikroTik, FortiGate, OPNsense) : l'URL désigne la ressource et le verbe HTTP (GET, POST, PUT, DELETE) désigne l'action.
2. JSON-RPC (ubus) : un seul point d'entrée /ubus en POST, l'action est dans le corps (objet, méthode, paramètres).
3. REST utilise les codes HTTP (200, 404, 401) pour signaler le résultat ; ubus répond toujours 200 et place un code d'erreur dans result[0].
4. Authentification REST : Basic Auth, clé/secret API ou token d'en-tête, envoyé à chaque requête.
5. Authentification ubus : un session.login explicite renvoie un ubus_rpc_session, à passer en premier paramètre de chaque appel suivant.
6. La session ubus expire et doit être renouvelée ; les APIs REST à clé sont sans état côté client.
7. Découverte REST : documentation Swagger/OpenAPI, URLs prévisibles, exploration facile avec un navigateur ou curl.
8. Découverte ubus : pas de documentation unifiée, il faut connaître les noms d'objets (network.interface, uci, system) et leurs méthodes.
9. Lisibilité : une URL REST se lit presque comme une phrase ; un appel ubus est plus verbeux mais très homogène (toujours la même structure).
10. Conclusion : REST est plus lisible et plus facile à explorer ; JSON-RPC/ubus est très léger et convient aux équipements embarqués à ressources limitées.
