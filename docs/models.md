# Models: the model table and model instances

Two structures tie things on the map to 3D models: a table of every model the save can use, and a model instance record for each placed thing that has one. The animals ([animals.md](animals.md)) and the hot air balloon ([fun-elements.md](fun-elements.md#the-model-instance)) use them. The fields match the `ModelInstanceList` component and `ModelInstance` record in `api/tealdef` (a model id, the transform at the previous frame, the transform). **Observed** on 604 in eighteen test saves (the animal test series of [terrain.md](terrain.md#what-was-compared) and others).

## The model table

The first thing after the header ([header.md](header.md)): a `u32` count, then per model

```
str  source mod (empty for the base game)
str  path
u32  id
```

- The ids run 0, 1, 2 and so on in table order. They are the index into the table, and they depend on the models installed, so read them from the save and do not carry them from one save to another.
- The base game's 4,473 models come first, sorted by path, so the 28 models under `animal/` are ids 0 to 27. A mod's models follow and carry the mod's id: `urbangames_deluxe_upgrade_pack` adds 31, among them `animal/bison/bison.mdl`, `animal/boar_m/boar_m.mdl` and `vehicle/zeppelin/hot_air_balloon/hot_air_balloon.mdl`.
- An earlier reading as `u64 id, str path` fits the base game's models only because their source string is empty: the previous entry's id and the next entry's empty string make eight bytes. The three-field layout is the right one.

## The model instance record

Somewhere after the header (2.7 to 3.9 MB in the animal test saves) there is one record per placed thing that has a model: a `u32` count of instances, then the instances.

- An instance is 137 bytes. It starts with the `u32` model id, then two 4 x 4 `f32` matrices one byte apart, with the translation in floats 12 to 14. In the instances read, both matrices held the same translation. The other bytes of an instance are **Open**.
- In the animal records the count is one for the animal plus one per flock offset, and 9 bytes separate one record's last instance from the next count (146 bytes for an animal without a flock). The first instance's translation equals the animal's `worldPosition`.
- **Find a record** by searching for the 12 bytes of a known position (as `f32` x, y, z) and reading the model id as the `u32` 52 bytes before it. The balloon's record was found this way.
- The records of the animals are in the order of the animal list. A record for a thing that has left the map is gone: no instance used the balloon's model after it had flown off.

Whether a vehicle keeps its model in a record of this kind is **Open** ([entity-names.md](entity-names.md#not-found)).
