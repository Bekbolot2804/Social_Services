class SectionType(DjangoObjectType):
    class Meta:
        model = Section
        fields = ('id', 'title', 'description', 'location', 'date', 'instructor', 'duration', 'imageUrl')


class Query(graphene.ObjectType):
    section = graphene.Field(SectionType, id=graphene.Int(required=True))

    def resolve_section(self, info, id):
        return Section.objects.get(pk=id)


class CreateSection(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)

    section = graphene.Field(SectionType)

    def mutate(self, info, title):
        section = Section.objects.create(title=title)
        section.save()
        return CreateSection(section=section)

class Mutation(graphene.ObjectType):
    create_section = CreateSection.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)