from rest_framework import generics, status
from .serializers import InventarioModel, InventarioSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.shortcuts import get_object_or_404


class InventariosView(generics.ListCreateAPIView):
    # Algunos atributos de la clase generica son:
    queryset = InventarioModel.objects.all()  # Select * from t_inventario
    serializer_class = InventarioSerializer

    def post(self, request):
        # Para capturar todo lo que me manda el cliente por el body, uso el request .data
        inventario = self.serializer_class(data=request.data)
        # Si se quiere usar el método is_valid OBLIGATORIAMENTE se tiene que pasar al constructor del serializador el parámetro data si no nos dará un error
        inventario.is_valid(raise_exception=True)
        # print('Todo bien, todo correcto.')
        # El save hace el guardado de mi información en la bd
        inventario.save()
        return Response({
            'ok': True,
            'content': inventario.data
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        # Si nosotros queremos pasar mas de una instancia al serializador (una lista de instancias) tendremos que declarar su parámetro many=True para que internamente haga la iteracion y puedan entender lo que le estamos pasando
        resultado = self.serializer_class(
            instance=self.get_queryset(), many=True)
        print(resultado.data)
        return Response({
            'ok': True,
            'content': resultado.data
        })


class InventarioView(generics.RetrieveUpdateDestroyAPIView):
    # La clase RetrieveUpdateDestroyAPIView me permite usar los metodos GET, PUT, DELETE
    queryset = InventarioModel.objects.all()
    serializer_class = InventarioSerializer

    def get(self, request, inventario_id):
        # SELECT * FROM t_inventario WHERE inventario_id=var
        # Al usar el first ya no retornará una lista sino que retornará un objeto, es la única claúsula de filtros que retorna un objeto
        inventario = self.queryset.filter(inventarioId=inventario_id).first()
        # SEGUNDA FORMA
        # Otra forma de hacer select pero mas delicada
        # Al momento de usar get tenemos que estar seguros que nos va a pasar un campo incorrecto porque sino crasheará el programa
        # try:
        #     print(self.queryset.get(inventarioId=inventario_id))
        # except:
        #     raise ParseError('Errorrrr!')
        # TERCERA FORMA
        # Se usa el método del propio django
        # Si encuentra un objeto con ese filtro lo retornará, si no automaticamente retornará un estadp 404
        # Lo que retorno es un objeto NO SERALIZADO
        # inventarioObject = get_object_or_404(InventarioModel, pk=inventario_id)
        inventarioSerializado = self.serializer_class(
            instance=inventario)
        return Response({
            'ok': True,
            'content': inventarioSerializado.data
        })

    def put(self, request, inventario_id):
        inventarioEncontrado = self.get_queryset().filter(
            inventarioId=inventario_id).first()
        print(inventarioEncontrado)
        inventarioUpdate = self.serializer_class(data=request.data)
        inventarioUpdate.is_valid(raise_exception=True)
        # luego que llamamos al metodo is_valid este aparte de devolver si es válido o no (bool) nos creará un diccionario con ña data correctamente validada siendo sus llames los nombre de las columnas y sus valores la data validada
        # Para usar el validate_data tenemos que llamar previamente al método is_valid() OBLIGA>TORIAMENTE
        resultado = inventarioUpdate.update(inventarioEncontrado,
                                            inventarioUpdate.validated_data)
        print(resultado)
        serializador = self.serializer_class(resultado)
        return Response({
            'ok': True,
            'content0': serializador.data,
            'message': 'Se actualizó el inventario exitosamente.'
        }, status=status.HTTP_201_CREATED)

    def delete(self, request, inventario_id):
        inventario = get_object_or_404(InventarioModel, pk=inventario_id)
        # El método delete es propio del ORM de django en el cual su clausula SQL sería:
        # delete from t_inventario where inventario_id=pk
        inventario.delete()
        return Response({
            'ok': True,
            'message': 'Se eliminó exitosamente el platillo',
            'content': None
        })
