import graphene
from graphene_django import DjangoObjectType

from lab1_app.models import Component


class ComponentType(DjangoObjectType):
    class Meta:
        model = Component
        fields = ('id', 'title', 'shortDescription', 'description', 'price', 'is_active', 'imgSrc')


class Query(graphene.ObjectType):
    component = graphene.Field(ComponentType, id=graphene.Int(required=True))

    def resolve_component(self, info, id):
        return Component.objects.get(pk=id)


class CreateComponent(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        price = graphene.Int(required=True)
        short_description = graphene.String(required=False)
        description = graphene.String(required=False)

    component = graphene.Field(ComponentType)

    def mutate(self, info, title, price, short_description, description):
        component = Component.objects.create(
            title=title,
            price=price,
            shortDescription=short_description,
            description=description
        )
        return CreateComponent(component=component)


class Mutation(graphene.ObjectType):
    create_component = CreateComponent.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)