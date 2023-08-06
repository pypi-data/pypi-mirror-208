import numpy as np
from graphviz import Digraph
from prettytable import PrettyTable

class HoodHod:
    class SimpleLinearRegression:
      def __init__(self):
        self.slope = None
        self.intercept = None
        

      def fit(self, X, y):
        n = len(X)
        mean_x, mean_y = sum(X) / n, sum(y) / n
        numer = sum([(xi - mean_x) * (yi - mean_y) for xi, yi in zip(X, y)])
        denom = sum([(xi - mean_x) ** 2 for xi in X])
        if denom == 0:
            self.slope = 0
        else:
            self.slope = numer / denom
        if numer == 0:
            self.intercept = 0
        else:
            self.intercept = mean_y - self.slope * mean_x

      def predict(self, X):
        return [self.slope * xi + self.intercept for xi in X]

      def r_squared(self, X, y):
        y_mean = sum(y) / len(y)
        y_pred = self.predict(X)
        ss_tot = sum([(yi - y_mean) ** 2 for yi in y])
        ss_res = sum([(yi - y_pred[i]) ** 2 for i, yi in enumerate(y)])
        return 1 - (ss_res / ss_tot)

      def mse(self, X, y):
        y_pred = self.predict(X)
        n = len(y)
        return sum([(yi - y_pred[i]) ** 2 for i, yi in enumerate(y)]) / n
    
    class BinaryDecisionTree:
      def __init__(self,X,y,features ,criterion='gini', random_state=None):
        self.X=X
        self.y=y
        self.features=features
        self.criterion = criterion
        self.random_state = random_state

      def calculate_entropy(self, y):
        entropy = 0
        unique_labels = np.unique(y)
        for label in unique_labels:
            count = len(y[y == label])
            p = count / len(y)
            entropy -= p * np.log2(p)
        return entropy
    
      def calculate_gini(self, y):
        gini = 1
        unique_labels = np.unique(y)
        for label in unique_labels:
            count = len(y[y == label])
            p = count / len(y)
            gini -= p ** 2
        return gini
    
      def fit(self):
        self.tree_ = self._build_tree(self.X, self.y, self.features, depth=0)
        return self.tree_
      def _build_tree(self, X, y,features, depth):
        n_features_ = X.shape[1]
        best_entropy = 1
      
        if len(np.unique(y)) == 1:    
           return{'class': y[0]}

        if len(X) == 0:
            return { 'class': None}

        best_feature=None
        for feature in range(n_features_):
                left = y[X[:, feature] == 0]
                right = y[X[:, feature] == 1]
                if len(left) == 0 or len(right) == 0:
                    continue
                if self.criterion == 'gini':
                    feature_entropy = (len(left) / len(y)) * self.calculate_gini(left) + (len(right) / len(y)) * self.calculate_gini(right)
                else:
                   
                    feature_entropy = (len(left) / len(y)) * self.calculate_entropy(left) + (len(right) / len(y)) * self.calculate_entropy(right)
                if best_entropy > feature_entropy:
                    best_feature = features[feature]
                    best_entropy = feature_entropy
                    best_feature_indice=feature

        if best_feature is None:
            leaf= { 'class': np.bincount(y).argmax()}
            return leaf 
        
        Xleft = X[X[:, best_feature_indice] == False]
        Xright = X[X[:, best_feature_indice] == True]
        
        yleft = y[X[:, best_feature_indice] == False]
        yright = y[X[:, best_feature_indice] == True]
        
        Xleft=np.concatenate((Xleft[:, :best_feature_indice], Xleft[:,best_feature_indice+1:]), axis=1)
        Xright=np.concatenate((Xright[:, :best_feature_indice], Xright[:,best_feature_indice+1:]), axis=1)
        
        features = np.delete(features, best_feature_indice)

        return {'feature': best_feature,
                'False': self._build_tree(Xleft,yleft,features, depth + 1),
                'True':self. _build_tree(Xright,yright,features, depth + 1)}
      def predict(self, X):
        predictions = []
        for sample in X:
          node = self.tree_
          while True:
            if 'feature' in node:
                if sample[self.features.index(node['feature'])]:
                    node = node['True']
                else:
                    node = node['False']
            else:
                predictions.append(node['class'])
                break
        return np.array(predictions)
      def visualize_tree(self, tree_dict, feature_names=None):
          dot = Digraph()
          def traverse_tree(node, node_name=None):
            if node_name is None:
              node_name = str(id(node))
            if 'class' in node:
               dot.node(node_name, label=str(node['class']))
            else:
                dot.node(node_name, label=node['feature'])
                left_node_name = str(id(node['False']))
                dot.edge(node_name, left_node_name, label='False')
                traverse_tree(node['False'], node_name=left_node_name)
                right_node_name = str(id(node['True']))
                dot.edge(node_name, right_node_name, label='True')
                traverse_tree(node['True'], node_name=right_node_name)

          traverse_tree(tree_dict)
          if feature_names is not None:
           for i, feature_name in enumerate(feature_names):
               dot.node('X'+str(i), label=feature_name, shape='plaintext')
               dot.edge('X'+str(i), str(id(tree_dict)))
          dot.render('decision_tree', format='png')
          dot.view()

      class EvaluationMetrics:
        def __init__(self, y_true, y_pred):
           self.y_true = y_true
           self.y_pred = y_pred
           self.tp, self.tn, self.fp, self.fn = self._calculate_confusion_matrix()

        def _calculate_confusion_matrix(self):
           tp = np.sum((self.y_true == 1) & (self.y_pred == 1))
           tn = np.sum((self.y_true == 0) & (self.y_pred == 0))
           fp = np.sum((self.y_true == 0) & (self.y_pred == 1))
           fn = np.sum((self.y_true == 1) & (self.y_pred == 0))
           return tp, tn, fp, fn
        def accuracy(self):
           return (self.tp + self.tn) / (self.tp + self.tn + self.fp + self.fn)
        
        def precision(self):
           if self.tp + self.fp == 0:
              return 0
           else:
              return self.tp / (self.tp + self.fp)

        def recall(self):
           if self.tp + self.fn == 0:
             return 0
           else:
             return self.tp / (self.tp + self.fn)
        def f1_score(self):
          p = self.precision()
          r = self.recall()
          if (p+r ==0):
             return 0
          else:
             return 2 * (p * r) / (p + r)

       
        def confusion_matrix(self):
         table = PrettyTable()
         table.field_names = ["", "Predicted Negative Values", "Predicted Positive Values"]
         table.add_row(["Actual Negative Values", self.tn, self.fp])
         table.add_row(["Actual Positive Values", self.fn, self.tp])
         return str(table)
        
        







