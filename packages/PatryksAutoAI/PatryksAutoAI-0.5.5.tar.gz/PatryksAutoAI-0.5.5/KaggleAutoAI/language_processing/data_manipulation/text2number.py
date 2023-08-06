import tensorflow as tf

class Text2Number():
    def __init__(self):
        self.token = None

    def tokenize(self, data, tokenizer, max_lenght):
        token = tokenizer(data.tolist(),
                          max_lenght=max_lenght,
                          truncation=True,
                          padding='max_length',
                          add_special_tokens=True,
                          return_tensors="tf")
        self.tokens = token

    def create_dataset(self, labels, batch_size=32):
        dataset = tf.data.Dataset.from_tensor_slices((self.token['input_ids'], self.token['attention_mask'], labels))
        dataset = dataset.map(self.map_func)
        dataset = dataset.shuffle(10000).batch(batch_size,drop_remainder=True)
        return dataset
    
    def map_func(self, input_ids, masks, labels):
        return {'input_ids':input_ids,
                'attention_mask':masks}, labels
    