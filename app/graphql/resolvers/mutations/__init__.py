from ariadne import MutationType

from .user_mutations import mutation as user_mutation
from .integration_mutations import mutation as integration_mutation
from .environment_mutations import mutation as environment_mutation
from .environment_types_mutations import mutation as environment_type_mutation

mutation_resolvers = MutationType()

for m in [user_mutation, integration_mutation, environment_mutation, environment_type_mutation]:
    for name, resolver in m._resolvers.items():
        mutation_resolvers.set_field(name, resolver)
