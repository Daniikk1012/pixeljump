class Wrapper:
    def __init__(self, v):
        self.v = v

class Parent(Wrapper): pass

class Entity:
    def __init__(self):
        # world is expected to be set by the container World
        self.components = {}

    def add(self, component):
        self.components[type(component)] = component
        return self

    def get(self, component):
        return self.components[component]

    def has(self, component):
        return component in self.components

    def remove(self, component):
        value = self.components[component]
        del self.components[component]
        return value

    def despawn(self):
        # Cleanup is done to prevent accidental use-after-free
        del self.components
        del self.world.entities[
            next(i for i, e in enumerate(self.world.entities) if e is self)
        ]
        del self.world

    def despawnall(self):
        for child, parent in self.world.iter(Parent):
            if p.v is self:
                child.despawnall()
        self.despawn()

class World:
    def __init__(self):
        self.resources = {}
        self.entities = []
        self.systems = []
        self.ordered = []

    def add(self, resource):
        self.resources[type(resource)] = resource
        return self

    def get(self, resource):
        return self.resources[resource]

    def has(self, resource):
        return resource in self.resources

    def remove(self, resource):
        value = self.resources[resource]
        del self.resources[resource]
        return value

    def spawn(self):
        entity = Entity()
        entity.world = self
        self.entities.append(entity)
        return entity

    def query(self, *args):
        match args:
            case []:
                return list(self.entities)
            case [component]:
                return [(entity, entity.get(component))
                    for entity in self.entities if entity.has(component)]
        return [(entity, tuple(entity.get(component) for component in args))
            for entity in self.entities
                if all(entity.has(component) for component in args)]

    def query_single(self, *args):
        query = self.query(*args)
        if len(query) > 1:
            raise RuntimeError('more than one entity')
        return query[0]

    def _invalidate_systems(self):
        systems = self.systems.copy()
        ordered = []
        while systems:
            for index, (system, after, before) in enumerate(systems):
                if (all(all(s is not a for (s, _, _) in systems) for a in after)
                    and all(all(s is not system for s in b)
                        for (_, _, b) in systems)
                ):
                    ordered.append((system, after, before))
                    del systems[index]
                    break
        self.ordered = [s for (s, _, _) in ordered]

    def system(self, system, *, after=[], before=[]):
        if any(s is system for (s, _, _) in self.systems):
            raise ValueError('system already in world')
        self.systems.append((system, after, before))
        self._invalidate_systems()
        return self

    def unsystem(self, system):
        try:
            del self.systems[next(i for i, (s, _, _) in enumerate(self.systems)
                if s is system
            )]
            self._invalidate_systems()
        except StopIteration:
            pass
        return self

    def run(self):
        for system in list(self.ordered):
            system(self)
