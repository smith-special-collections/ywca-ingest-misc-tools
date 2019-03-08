This tool takes a list of object files and looks for them on
Compass. If it doesn't find a matching object, or if it finds more than one
object, it returns an error. The local id of the object is derivied from the
file naming pattern. This id is used to query the mods_identifier_local_s field
in Solr.

Note: for access to the Solr server you will probably need to be logged into
the Hampshire VPN.
