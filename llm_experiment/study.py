import tokenizers
import tokenizers.decoders

a= tokenizers("게이게이어 이렇게 어 게이 어 [[]]")

print(a)

b= tokenizers.decoders(a)

print(b)
