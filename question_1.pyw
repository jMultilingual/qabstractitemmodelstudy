from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
import os, sys
import PySide2
import sqlite3
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=None)        
        self.sequoiaview = SequoiaView()
        self.baobabview = BaobabView()
        self.sequoiaview._baobabview = self.baobabview
        self.baobabview._sequoiaview = self.sequoiaview
        self.sequoiamodel = SequoiaModel(parent=self.sequoiaview)
        self.sequoiaview.setModel(self.sequoiamodel)
        self.baobabmodel = BaobabModel(parent=self.baobabview)
        self.baobabview.setModel(self.baobabmodel)
        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.sequoiaview)
        layout.addWidget(self.baobabview)
        central.setLayout(layout)
        self.setCentralWidget(central)
class SequoiaView(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(SequoiaView, self).__init__(parent=None)      
        self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.ExtendedSelection)   
        self.setSelectionBehavior(QtWidgets.QTreeView.SelectionBehavior.SelectRows)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)  
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)        
        self.startDragPosition = QtCore.QPoint()
        self.setAnimated(True)
        self.setRootIsDecorated(True)
        self.clicked["QModelIndex"].connect(self.retrievedata)        
        self.preIndex = QtCore.QModelIndex()
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()            
        return QtWidgets.QTreeView.dragEnterEvent(self, event)
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):            
            index = self.indexAt(event.pos())
            if not index.isValid():
                return
            else:                
                event.accept()
            self.retrievedata(index)
            self.preIndex = index
        return QtWidgets.QTreeView.dragMoveEvent(self, event)     
        
    def retrievedata(self, index):
        con = sqlite3.connect("temp_haru.db")
        with con:
            cur = con.cursor()     
            currentIndex = self.currentIndex()      
            print(index)
            if self.preIndex != index:
                self.preIndex = currentIndex           
                wmodel = self._baobabview.model()          
                rootIndex = self._baobabview.rootIndex()
                print(rootIndex)
                m = wmodel.removeRows(0, wmodel.rowCount())      
                internalPointer = currentIndex.internalPointer()
                cur.execute("SELECT * FROM BAOBAB WHERE ID = ?", (int(internalPointer._data[SequoiaModel.ID]),))
                baobabs = cur.fetchall()    
                dic = {i[BaobabModel.WID]: BaobabItem(list(i), QtGui.QIcon(), None) for i in baobabs}         
                values = dic.values()
                for v in values:               
                    pid = v._data[BaobabModel.PID]                    
    #                    wmodel.insertRows(0, 1, QtCore.QModelIndex(), [v])   
                                 
                    if pid == -1:
#                        wmodel.beginInsertRows(rootIndex, len(wmodel.root.children),len(wmodel.root.children)+1 )
                        w = wmodel.root.insertChild(len(wmodel.root.children), v, is_locked=False)
#                        wmodel.endInsertRows()
                    else:                        
                        parent = dic[pid]  
                        
#                        wmodel.beginInsertRows(len(parent.children), len(parent.children)+1)
                        w = parent.insertChild(len(parent.children), v, is_locked=False)     
#                        wmodel.endInsertRows()                             
                wmodel.emit(QtCore.SIGNAL("dataChanged(QModelIndel*, QModelIndex*)"))
                wmodel.emit(QtCore.SIGNAL("layoutChanged()"))        
                
            
class BaobabView(SequoiaView):
    def __init__(self, parent=None):
        super(BaobabView, self).__init__(parent)
    def retrievedata(self, index):
        print(index)
    def dragEnterEvent(self, event):
        return QtWidgets.QTreeView.dragEnterEvent(self, event)
    def dragMoveEvent(self, event):
        return QtWidgets.QTreeView.dragMoveEvent(self, event)

class SequoiaModel(QtCore.QAbstractItemModel):
    NAME = 0
    ID = 1
    WID = 2
    PID = 3
    def __init__(self, items = [], parent=None):
        super(SequoiaModel, self).__init__(parent=None)        
        self._switch = False
        self.__parent = parent        
        self.root = SequoiaItem(["root", -1, -1, -1], QtGui.QIcon(), None)        
        if items:
            for i in items:
                self.root.addChild(i)   
        defaultItems1 = [SequoiaItem(["sequoia{0}".format(i), i, i, -1], QtGui.QIcon(), self.root) for i in range(5)]
        defaultItems2 = [SequoiaItem(["sequoia{0}".format(i), i, i, -1], QtGui.QIcon(), self.root) for i in range(5, 10)]
        defaultItems3 = [SequoiaItem(["sequoia{0}".format(i), i, i, -1], QtGui.QIcon(), self.root) for i in range(10, 15)]
        con = sqlite3.connect("temp_haru.db")
        with con:
            cur = con.cursor()
            
            for i in range(5):
                self.root.addChild(defaultItems1[i])
                cur.execute("INSERT INTO SEQUOIA VALUES(?, ?, ?, ?)", defaultItems1[i]._data)
            for num, i in enumerate(defaultItems1):
                i.addChild(defaultItems2[num])
                cur.execute("INSERT INTO SEQUOIA VALUES(?, ?, ?, ?)", defaultItems2[num]._data)
            for num, i in enumerate(defaultItems2):
                i.addChild(defaultItems3[num])
                cur.execute("INSERT INTO SEQUOIA VALUES(?, ?, ?, ?)", defaultItems3[num]._data)
#            cur.execute("SELECT * FROM SEQUOIA")
#            m = cur.fetchall()
#            print(137, m)
        self.emit(QtCore.SIGNAL("dataChanged(QModelIndex*, QModelIndex*)"))
        self.emit(QtCore.SIGNAL("layoutChanged"))
        self.max_id = len(items) 
        self.expandlist = []
        self.droppedMimeDataIndexHasNoChildren = None   
        self.droppedMimeDataIndexes = None       
    def rowCount(self, parent=QtCore.QModelIndex()):
        if not parent.isValid():
            r = self.root   
            return r.childCount()
        else:
            r = parent.internalPointer()            
            return r.childCount()
    def columnCount(self, parent=QtCore.QModelIndex()):
        return 4
    def flags(self, index):         
        return QtCore.Qt.ItemFlag.ItemIsDragEnabled|QtCore.Qt.ItemIsDropEnabled|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled        
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Orientation.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return "NAME"
                elif section == 1:
                    return "ID"   
                elif section == 2:
                    return "WID"
                elif section == 3:
                    return "PID"
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        treeitem = index.internalPointer()        
        if role == QtCore.Qt.DisplayRole:
            column = index.column()            
            return treeitem._data[column]
        elif role == QtCore.Qt.DecorationRole:
            column = index.column()
            if column == 0:
                return treeitem.icon   
        elif role == QtCore.Qt.ItemDataRole.CheckStateRole:
            column = index.column()
            if column == 0:
                return False
   
    def index(self, row, column , _parent = QtCore.QModelIndex()):
        if not _parent.isValid():
            parent = self.root
        else:
            parent = _parent.internalPointer()
        if not self.hasIndex(row, column, _parent):
            return QtCore.QModelIndex()
        child = parent.child(row)        
        if child:
            childIndex = self.createIndex(row, column, child)      
            return childIndex
        else:
            return QtCore.QModelIndex()
    def parent(self, child):
        if not child.isValid():
            return QtCore.QModelIndex()   
        try:            
            treeitem = child.internalPointer()           
            parent = treeitem.parent()           
            if parent is not None:
                parentindex = self.createIndex(treeitem.at(), 0, parent)    
                return parentindex
            else:
                return QtCore.QModelIndex()
        except AttributeError as e:
            print(e)
            return QtCore.QModelIndex()        
    def supportedDragActions(self):        
        return  QtCore.Qt.MoveAction
    def supportedDropActions(self):
        return QtCore.Qt.MoveAction
    def mimeTypes(self):
        return ["application/x-qabstractitemmodeldatalist"]
    def mimeData(self, indexes): 
        if not indexes:
            return 0             
        mimedata = QtCore.QMimeData()            
        datas = self.serializedData(indexes)              
        mimedata.setData("application/x-qabstractitemmodeldatalist", datas)   
        return mimedata        
    def serializedData(self, indexes):
        blob = QtCore.QByteArray()
        out = QtCore.QDataStream(blob, QtCore.QIODevice.WriteOnly)       
        indexes_col0 = [i for i in indexes if i.column() == 0]
        self.droppedMimeDataIndexes = indexes_col0      
        indexes_parentChildren = [i for i in indexes_col0 if i.parent().internalPointer() not in [i.internalPointer() for i in indexes_col0 if i.isValid()] and i.parent().isValid() and i.isValid()]
        self.droppedMimeDataIndexHasNoChildren = indexes_parentChildren        
        for i in self.droppedMimeDataIndexHasNoChildren:
            p = i.internalPointer()
            stringList = [str(k) for k in p._data]    
            out.writeQStringList(stringList)
            out << p.icon
        return blob
    def insertSubDirectories(self, idx, children):
        for num, child in enumerate(children):
            a = idx.child(num, 0)
            ai = child.children                              
            self.insertRows(0, len(ai), a, ai)
            self.insertSubDirectories(a, ai)  
    def getExpandSubdirectories(self, idx, children):
        for num, child in enumerate(children):
            a = idx.child(num, 0)
            if self.__parent.isExpanded(a) and int(a.internalPointer()._data[1]) not in self.expandlist:
                self.expandlist.append(int(a.internalPointer()._data[1]))                
            ai = child.children                              
            self.getExpandSubdirectories(a, ai)
    def expandSubdirectories(self, idx, children):
        for num, child in enumerate(children):
            a = idx.child(num, 0)
            if a.internalPointer() is not None:                
                if int(a.internalPointer()._data[1]) in self.expandlist:
                    self.__parent.setExpanded(a, True)
            ai = child.children
            self.expandSubdirectories(a, ai)        
    def dropMimeData(self, data, action, row, column, parent):
        #dropIndicatorPositionがOnItemのとき、parentは入れこみ先のアイテムを指す。
        #それ以外の時、parentは入れ込んだ階層の親となる。
        if action == QtCore.Qt.IgnoreAction:
            return True        
        if not data.hasFormat("application/x-qabstractitemmodeldatalist"):
            return False
        if column > 0:
            return False        
        self.__parent.selectAll()
        selectedIndexes = self.__parent.selectedIndexes()    
        #現在展開中のアイテムのIDを取得             
        self.expandlist = [int(i.internalPointer()._data[1]) for i in selectedIndexes if self.__parent.isExpanded(i) and len(selectedIndexes) != 0]
        for num, idx in enumerate(selectedIndexes):
            children = idx.internalPointer().children
            self.getExpandSubdirectories(idx, children)       
        byteArray = QtCore.QByteArray(data.data("application/x-qabstractitemmodeldatalist"))
        out = QtCore.QDataStream(byteArray , QtCore.QIODevice.ReadOnly)        
        newItems = []                   
        if row != -1:                
            beginRow = row
            parentItem = parent.internalPointer() 
        elif self.__parent.dropIndicatorPosition() == QtWidgets.QAbstractItemView.OnItem:         
            beginRow = self.rowCount(parent)         
            parentItem = parent.internalPointer()                
        else:            
            beginRow = self.rowCount(parent)             
            parentItem = parent.internalPointer()                   
        rows = 0     
        while not out.atEnd():
            text = out.readQStringList()
            intel = []
            for i in text:
                if i.isdigit():
                    intel.append(int(i))
                else:
                    intel.append(i)
            text = intel
            icon = QtGui.QIcon()
            out >> icon
            newItem = SequoiaItem(text, icon, parentItem)               
            newItems.append(newItem)            
            rows += 1      
        
        
        startRow = beginRow
        self.insertRows(beginRow, rows, parent, newItems)     
        beginRow = startRow
        for i in newItems:                         
            idx = self.index(beginRow, 0, parent)               
            i._modelindex = idx
            self.setData(idx, i)
            beginRow += 1            
        self.__parent.clearSelection()
        print(308, self.droppedMimeDataIndexHasNoChildren)
        for num, index in enumerate(self.droppedMimeDataIndexHasNoChildren): 
            #This code causes unexpected error. index is sometimes not QModelIndex... and internalPointer become sometimes a QModelIndex, list object, list-iterator, socket in spite of the same handling.
            originalPointer = index.internalPointer()   
            if not isinstance(originalPointer, (QtGui.QIcon, QtCore.QModelIndex)):                                 
                originalchildren = originalPointer.children
                if originalchildren:
                    for new in newItems:
                        if int(originalchildren[0]._data[BaobabModel.PID]) == int(new._data[BaobabModel.WID]):
                            idx = new._modelindex         
                    if self.__parent.dropIndicatorPosition() == QtWidgets.QAbstractItemView.OnItem:
                        self.insertRows(0, len(originalchildren), idx, originalchildren)
                    else:                            
                        self.insertRows(startRow, len(originalchildren), idx, originalchildren)
                    self.insertSubDirectories(idx, originalchildren)      
        #This code is obstacled when other tree items come because items have been already removed by retrievedata.
#        for num, i in enumerate(self.droppedMimeDataIndexes):
#            item = self.nodeFromIndex(i)
#            i_parent = i.parent()
#            pitem = self.nodeFromIndex(i_parent)
#            i_row = pitem.children.index(item) 
#            self.removeRow(i_row, i_parent)
#    
        self.__parent.selectAll()
        selectedIndexes = self.__parent.selectedIndexes()    
        for i in selectedIndexes:
            internalPointer = i.internalPointer()
            number = internalPointer._data[1]
            if int(number) in self.expandlist:
                self.__parent.expand(i)
                self.expandSubdirectories(i, internalPointer.children)
        self.__parent.clearSelection()                       
        return False
    def insertRows(self, position, count, parent = QtCore.QModelIndex(), fromDropMimeData=None):     
        success = False        
        if not parent.isValid():
            parentitem = self.root
        else:            
            parentitem = parent.internalPointer()   
        self.beginResetModel()
        self.beginInsertRows(parent, position, position+count-1)     
        for i in range(0, count):    
            if fromDropMimeData is not None:
                if type(self) == BaobabModel:
                    """BaobabItem & SequoiaItem is the same content now."""
                    item = BaobabItem(fromDropMimeData[i]._data , fromDropMimeData[i].icon, parentitem)       
                
                else:
                    item = SequoiaItem(fromDropMimeData[i]._data , fromDropMimeData[i].icon, parentitem)                       
            else:                
                item = SequoiaItem([":Empty:", -1], QtGui.QIcon(), parentitem)
            success = parentitem.insertChild(position+i, item, False)
        self.endInsertRows()     
        self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), parent, parent)
        self.emit(QtCore.SIGNAL("layoutChanged()"))        
        self.endResetModel()
        return success
    def removeRows(self, position, count , parent=QtCore.QModelIndex()):     
        success = False        
        if not parent.isValid():
            parentitem = self.root
        else:       
            parentitem = parent.internalPointer()        
        items = parentitem.children[position: position + count]   
        if items:          
            self.beginResetModel()
            self.beginRemoveRows(parent, position, position + count - 1)
            success = parentitem.removeChildren(position, count)                      
            self.endRemoveRows()
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), parent, parent)
            self.emit(QtCore.SIGNAL("layoutChanged()"))      
            self.endResetModel()
        return success
    def moveRows(self, sourceParent=QtCore.QModelIndex(), sourceFirst = 0, sourceLast = 0, destinationParent=QtCore.QModelIndex(), destinationRow=0):
        """Under Construction"""
        success = False
        if not sourceParent.isValid():
            sourceparentitem = self.root
        else:
            sourceparentitem = sourceParent.internalPointer()      
        if not destinationParent.isValid():
            destinationitem = self.root
        else:
            destinationitem = destinationParent.internalPointer()
        if sourceparentitem is destinationitem and sourceFirst == destinationRow:
            return success      
        movedItems = sourceparentitem.movedItems(sourceFirst, sourceLast)        
        if movedItems:         
            self.beginMoveRows(sourceParent, sourceFirst, sourceLast, destinationParent, destinationRow)  
            for i in movedItems:
                sourceparentitem.removeChild(i)            
              
            success = destinationitem.insertChildren(destinationRow, len(movedItems), movedItems)                
            self.endMoveRows()                      
        else:
            pass
        return success
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:                    
            if isinstance(value, SequoiaItem):                
                item = self.nodeFromIndex(index.parent())   
                row = index.row()
                item.children[row]._data = value._data
                item.children[row].icon = value.icon
                self.dataChanged.emit(index, index)         
                return True
            else:                
                item = self.nodeFromIndex(index.parent())                     
                item.children[index.row()]._data[index.column()] = value       
                self.dataChanged.emit(index, index)
                return True
            return False
        elif role == QtCore.Qt.DisplayRole:                    
            if isinstance(value, SequoiaItem):                
                item = self.nodeFromIndex(index.parent()) 
                row = index.row()
                item.children[row]._data = value._data   
                item.children[row].icon = value.icon
                self.dataChanged.emit(index, index)         
                return True
            else:    
                row = index.row()                
                item = self.nodeFromIndex(index.parent())
                item.children[row]._data[index.column()] = value    
                self.dataChanged.emit(index, index)
                return True
            return False
        return False
    def nodeFromIndex(self, index):        
        return index.internalPointer() if index.isValid() else self.root
    def indexFromNode(self, node):
        return node._modelindex
class BaobabModel(SequoiaModel):
    NAME = 0
    ID = 1    
    WID = 2
    PID = 3
    def __init__(self, items=[], parent=None):
        super(BaobabModel, self).__init__(items, parent)
        self.__parent = parent
        self.root = BaobabItem(["root", -1, -1, -1], QtGui.QIcon(), None)        
        if items is not None:
            for i in items:
                self.root.addChild(i)  
        defaultItems1 = [BaobabItem(["baobab{0}".format(i), 0, i, -1], QtGui.QIcon(), self.root) for i in range(5)]
        defaultItems2 = [BaobabItem(["baobab{0}".format(i), 0, i, -1], QtGui.QIcon(), self.root) for i in range(5, 10)]
        defaultItems3 = [BaobabItem(["baobab{0}".format(i), 0, i, -1], QtGui.QIcon(), self.root) for i in range(10, 15)]
        con = sqlite3.connect("temp_haru.db")
        with con:
            cur = con.cursor()
            for i in range(5):
                self.root.addChild(defaultItems1[i])
                cur.execute("INSERT INTO BAOBAB VALUES(?, ?, ?, ?)", defaultItems1[i]._data)
            for num, i in enumerate(defaultItems1):
                i.addChild(defaultItems2[num])
                cur.execute("INSERT INTO BAOBAB VALUES(?, ?, ?, ?)", defaultItems2[num]._data)
            for num, i in enumerate(defaultItems2):
                i.addChild(defaultItems3[num])
                cur.execute("INSERT INTO BAOBAB VALUES(?, ?, ?, ?)", defaultItems3[num]._data)
            cur.execute("SELECT * FROM BAOBAB")
            m = cur.fetchall()
            print(137, m)

        self.max_id = len(items) 
        self.expandlist = []
        self.droppedMimeDataIndexHasNoChildren = None   
        self.droppedMimeDataIndexes = None        
    def columnCount(self, parent=QtCore.QModelIndex()):
        return 4
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Orientation.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return "Tree"
                elif section == 1:
                    return "ID"      
                elif section == 2:
                    return "WID"
                elif section == 3:
                    return "PID"
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        treeitem = index.internalPointer()        
        if role == QtCore.Qt.DisplayRole:
            column = index.column()            
            return treeitem._data[column]
    
class SequoiaItem(object):
    def __init__(self, data, icon = QtGui.QIcon(), parent=None):
        super(SequoiaItem, self).__init__()
        self._data = data    
        self.icon = icon
        self.children = []
        self.baobabs = []
        self.row = 0
        self._parent = parent        
    def at(self):
        if self._parent is not None:
            if self in self._parent.children:                
                index = self._parent.children.index(self)
                return index
        return 0
    def child(self, row):
        if row < 0  or row > len(self.children)-1:
            return None
        child = self.children[row]        
        return child
    def childCount(self):
        return len(self.children)
    def addChild(self, item, is_locked=True):        
        item.setParent(self)       
        wid = self._data[SequoiaModel.WID]
        item._data[SequoiaModel.PID] = self._data[SequoiaModel.WID]
        if not is_locked:            
            con = sqlite3.connect("temp_haru.db")
            with con:
                cur = con.cursor()
                if type(self) == SequoiaItem:
                    cur.execute("UPDATE SEQUOIA SET PID = ? WHERE WID = ?", (wid, wid,))
                elif type(self) == BaobabItem:
                    cur.execute("UPDATE BAOBAB SET PID = ? WHERE WID = ?", (wid, wid,))
        self.children.append(item)
        return True
    
    def columnCount(self):
        return len(self._data)
    def data(self, column):
        if column < 0  or column >= self.columnCount():
            return None
        return self._data[column]
    def setData(self, column, value):        
        if column < 0  or column >= self.columnCount():
            return None
        self._data[column] = value
        return True
    def insertColumns(self, position, columns):
        if position < 0  or position >= self.columnCount():
            return False
        for column in range(0, columns):
            self._data.insert(position, None)
        for i in self.children:
            i.insert(position, columns)  
    def insertChild(self, insertrow, item, is_locked=True):        
        if item not in self.children:
            item.setParent(self)
            wid = self._data[SequoiaModel.WID]
            item._data[SequoiaModel.PID] = self._data[SequoiaModel.WID]
            self.children.insert(insertrow, item)    
            if not is_locked:
                con = sqlite3.connect("temp_haru.db")
                with con:
                    cur = con.cursor()
                    if type(self) == SequoiaItem:
                        cur.execute("UPDATE SEQUOIA SET PID = ? WHERE WID = ?", (wid,  wid,))
                    elif type(self) == BaobabItem:
                        cur.execute("UPDATE BAOBAB SET PID = ? WHERE  WID= ?", (wid, wid,))
            
            return True          
        else:
            return False
    def insertChildren(self, position, lastposition, datas):
        if position < 0  or lastposition >= self.columnCount():
            return False
        for n, i in enumerate(datas):
            if i in self.children:
                return False
            i.setParent(self)
            self.insertChild(position+n, i)
        return True    
    def removeChild(self, item):
        if item in self.children:
            self.children.remove(item)
            item.setParent(None)
            return True
        else:
            return False
    def removeChildren(self, position, count):
        if position < 0  or  position + count > len(self.children):
            return False
        removedItems = self.children[position: position + count]
        for i in removedItems:
            assert(i in removedItems)
            self.children.remove(i)
            i.setParent(None)
        return True
    def setParent(self, parent):
        self._parent = parent
            
    def parent(self):
        return self._parent
    def movedItems(self, row, lastRow):
        if (0 < self.childCount() or self.childCount() > lastRow) and row != lastRow:            
            movedItems = self.children[row : lastRow]
            return movedItems
        if row == lastRow:
            movedItems = self.children[row]
            return [movedItems]
        return []
class BaobabItem(SequoiaItem):
    def __init__(self, data, icon = QtGui.QIcon(), parent=None):
        super(BaobabItem, self).__init__(data, icon, parent)
        self._data = data     
        self.icon = icon
        self.children = []
        self.row = 0
        self._parent = parent
        self._modelindex = QtCore.QModelIndex()
    
def main():
    if QtWidgets.QApplication.instance() is not None:
        app = QtWidgets.QApplication.instance()
    else:
        app = QtWidgets.QApplication([])
    con = sqlite3.connect("temp_haru.db")
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS SEQUOIA")
        cur.execute("DROP TABLE IF EXISTS BAOBAB")
        cur.execute("CREATE TABLE IF NOT EXISTS SEQUOIA(NAME TEXT, ID INT, WID INT, PID INT)")
        cur.execute("CREATE TABLE IF NOT EXISTS BAOBAB(NAME TEXT, ID INT, WID INT, PID INT)")
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(QtWidgets.QApplication.exec_())
if __name__ == "__main__":
    main()
