[TOC]


# 作业提交与反馈(微信多对一辅导群)

## 第四课总结

回想链表的图像。在链表中，每个节点 pair 的第二个元素（second）都是一个 pair 或者 null。这样形成了「线性」的结构，所有元素都挂在 first 的位置，而 second 就类似于链条。first 就像下图中的筐子，里面可以放任意的元素。second 就像把这些筐子串起来的那些链条。链表之所以叫链表，就是因为这个链条。

链表实物图_形象:\
![[20210411220421112_8247.png]]

现在我们突破一下链表结构，形成「树结构」。在树结构里，first 不一定都是元素，而可能是另一个 pair 或者 null。second 也不都是 pair 或者 null，而可以是元素。总的说来，每一个 first 或者 second 都可以是 pair，null，或者元素。

比如我们可以有：
```js
var tree1 = pair(pair(2, 3), pair(4, 5));
var tree2 = pair(pair(2, 3), pair(4, pair(null, 5)));

// 原来的 pairToString 仍然可以用，为什么？
show(pairToString(tree1));
// ((2, 3), (4, 5))
show(pairToString(tree2));
// ((2, 3), (4, (null, 5)))
```

它们的图形表示如下：\
![[20210411220454763_12414.png]]

请注意，tree2 里面有一个 null，它表示那个 pair 的左边分支「不存在」。因为不存在，所以没有把它画出来，但你应该知道那个地方是一个 null。


使用类似之前对链表的公式化定义，我们可以这样定义这种简单的树：
- null 是一棵树。
- pair 也是树。

这种简单的树只有两个分叉，所以叫做「二叉树」。因为二叉树在语义上没有「头」和「尾」，而是有「左」和「右」，所以我们定义两个名字 left 和 right，它们分别是原来 pair 的 first 和 second 函数：

```js
var left = first;
var right = second;
```

我们可以对树进行类似链表的一些操作，比如求大小，求和，求积等。下面就是这类练习。

## size

写一个函数 size，它类似链表的 length 函数，返回的是二叉树里面元素的个数（不包括 pair 和 null）。
```js
var tree1 = pair(pair(2, 3), pair(4, 5));
var tree2 = pair(pair(2, 3), pair(4, pair(null, 5)));

function size(tree)
{
  // TODO
}

show("----- size -----");
show(size(tree1));    // 4
show(size(tree2));    // 4
```

**【SeaflyWechat】**\
老师您好，第 size 题提交如下：
```js
function pair(a, b)
{
    return f => f(a, b);
}

function first(p)
{
    return p((a, b) => a);
}

function second(p)
{
    return p((a, b) => b);
}

function isPair(p)
{
    return typeof(p) == "function";
}

var left = first;
var right = second;
var show = console.log;
var tree1 = pair(pair(2, 3), pair(4, 5));
var tree2 = pair(pair(2, 3), pair(4, pair(null, 5)));

function size(tree)
{
    if (tree == null)
    {
        return 0;
    }
    else if (! isPair(tree))
    {
        return 1;
    }
    else
    {
        return size(left(tree)) + size(right(tree));
    }
}

show("----- size -----");
show(size(tree1));    // 4
show(size(tree2));    // 4
```

**【SeaflyWechat】**\

**【SeaflyWechat】**\

**【SeaflyWechat】**\






## sumTree
写一个函数 sumTree，它把一棵二叉树里所有的数字加在一起。你可以假设这棵树里所有的元素都是数字，不需要检查其它类型。
```js
function sumTree(tree)
{
  // TODO
}

show("----- sumTree -----");
show(sumTree(tree1));    // 14
show(sumTree(tree2));    // 14
```


**【SeaflyWechat】**\
老师您好，第 sumTree 题提交如下：
```js
var left = first;
var right = second;
var show = console.log;
var tree1 = pair(pair(2, 3), pair(4, 5));
var tree2 = pair(pair(2, 3), pair(4, pair(null, 5)));

function sumTree(tree)
{
    if (tree == null)
    {
        return 0;
    }
    else if (! isPair(tree))
    {
        return tree;
    }
    else
    {
        return sumTree(left(tree)) + sumTree(right(tree));
    }
}

show("----- sumTree -----");
show(sumTree(tree1));    // 14
show(sumTree(tree2));    // 14

```

**【SeaflyWechat】**\

**【SeaflyWechat】**\

**【SeaflyWechat】**\


## prodTree
写一个函数 prodTree，它把一棵二叉树里所有的数字乘在一起。
```js
function prodTree(tree)
{
  // TODO
}

show("----- prodTree -----");
show(prodTree(tree1));    // 120
show(prodTree(tree2));    // 120
```

**【SeaflyWechat】**\
老师您好，第 prodTree 题提交如下：
```js
var left = first;
var right = second;
var show = console.log;
var tree1 = pair(pair(2, 3), pair(4, 5));
var tree2 = pair(pair(2, 3), pair(4, pair(null, 5)));

function prodTree(tree)
{
    if (tree == null)
    {
        return 1;
    }
    else if (! isPair(tree))
    {
        return tree;
    }
    else
    {
        return prodTree(left(tree)) * prodTree(right(tree));
    }
}

show("----- prodTree -----");
show(prodTree(tree1));    // 120
show(prodTree(tree2));    // 120
```

**【SeaflyWechat】**\

**【SeaflyWechat】**\





## foldTree
写一个函数 foldTree，类似于之前对于链表的 fold 函数，只是它是对于树结构的。当得到合适的参数，它能表示 sumTree 和 prodTree。
```js
function foldTree(tree, unit, combine)
{
  // TODO
}

function sumTree2(tree)
{
    return foldTree(___, ___, ___);
}

function prodTree2(tree)
{
    return foldTree(___, ___, ___);
}

show("----- foldTree -----");
show(sumTree2(tree1));     // 14
show(sumTree2(tree2));     // 14
show(prodTree2(tree1));    // 120
show(prodTree2(tree2));    // 120
```


**【SeaflyWechat】**\
老师，第 foldTree 题提交如下：
```js
var left = first;
var right = second;
var show = console.log;
var tree1 = pair(pair(2, 3), pair(4, 5));
var tree2 = pair(pair(2, 3), pair(4, pair(null, 5)));

function foldTree(tree, unit, combine)
{
    if (tree == null)
    {
        return unit;
    }
    else if (! isPair(tree))
    {
        return tree;
    }
    else
    {
        return combine(foldTree(left(tree), unit, combine), foldTree(right(tree), unit, combine));
    }
}

function sumTree2(tree)
{
    return foldTree(tree, 0, (a, b) => a + b);
}

function prodTree2(tree)
{
    return foldTree(tree, 1, (a, b) => a * b);
}

show("----- foldTree -----");
show(sumTree2(tree1));     // 14
show(sumTree2(tree2));     // 14
show(prodTree2(tree1));    // 120
show(prodTree2(tree2));    // 120
```


**【SeaflyWechat】**\

**【SeaflyWechat】**\

## mapTree
写一个函数 mapTree，它把 f 作用于树的每一个元素，形成一棵「同构」的树。
```js
function mapTree(f, tree)
{
}

show("----- mapTree -----");
show(pairToString(mapTree(x => x * 2, tree1)));
// ((4, 6), (8, 10))
show(pairToString(mapTree(x => x * x, tree2)));
// ((4, 9), (16, (null, 25)))
```


**【SeaflyWechat】**\
老师，第 mapTree 题提交如下：
```js
var left = first;
var right = second;
var show = console.log;
var tree1 = pair(pair(2, 3), pair(4, 5));
var tree2 = pair(pair(2, 3), pair(4, pair(null, 5)));

function mapTree(f, tree)
{
    if (tree == null)
    {
        return null;
    }
    else if (! isPair(tree))
    {
        return f(tree);
    }
    else
    {
        return pair(mapTree(f, left(tree)), mapTree(f, right(tree)));
    }
}

show("----- mapTree -----");
show(pairToString(tree1));
show(pairToString(tree2));
show(pairToString(mapTree(x => x * 2, tree1)));
// ((4, 6), (8, 10))
show(pairToString(mapTree(x => x * x, tree2)));
// ((4, 9), (16, (null, 25)))
```

**【SeaflyWechat】**\
总结：mapTree 返回一个新的树，既然是树，就需要用到 pair 来构造，从草稿图上看出，每棵树只有最底下的叶子节点是纯数字，所以这里递归的思路就是从叶子节点开始反向构造树，一层一层反向往上构造，最后构成一棵新的树。

**【SeaflyWechat】**\

## flatten

写一个函数 flatten，输入一棵二叉树，返回一个链表。这个链表里是树的所有元素，从左到右依次排列。flatten 的意思是“压平”，本来树是多级的有高度的结构，结果被变成一个链表，就好像被压平了。

提示：你可以使用 append 的帮助。
```js
function flatten(tree)
{
  // TODO
}

show("----- flatten -----");
show(pairToString(flatten(tree1)));
// (2, (3, (4, (5, null))))
show(pairToString(flatten(tree2)));
// (2, (3, (4, (5, null))))
```



**【SeaflyWechat】**\
老师，第 flatten 题提交如下：
```js
var left = first;
var right = second;
var show = console.log;
var tree1 = pair(pair(2, 3), pair(4, 5));
var tree2 = pair(pair(2, 3), pair(4, pair(null, 5)));

function flatten(tree)
{
    if (tree == null)
    {
        return null;
    }
    else if (! isPair(tree))
    {
        return pair(tree, null);
    }
    else
    {
        return append(flatten(left(tree)), flatten(right(tree)));
    }
}

show("----- flatten -----");
show(pairToString(flatten(tree1)));
// (2, (3, (4, (5, null))))
show(pairToString(flatten(tree2)));
// (2, (3, (4, (5, null))))

```



## listToString
之前的 pairToString 函数，可以显示所有用 pair 实现的结构。pairToString 其实是一个对于树的递归函数。用 pairToString 来显示链表结构，结果是比较繁复的，因为里面有太多括号，所以我们把 pairToString 改写为一种专门针对链表的函数，叫 listToString。

我把 pairToString 的定义重复在这里，你可以从它出发来设计 listToString。
```js
function pairToString(x)
{
  if (! isPair(x)) 
  {
    return String(x);
  }
  else 
  {
    return "(" 
      + pairToString(first(x)) 
      + ", " 
      + pairToString(second(x))
      + ")";
  }
}

var list1 = pair(7, pair(3, pair(2, pair(9, null))));
show(pairToString(list1));
// (7, (3, (2, (9, null))))
```
listToString 针对 pairToString 的不同点主要在于：当 second 是 pair 的时候，它不显示 second 两边的括号，也不显示中间的分隔符（这里是逗号）。

另外，listToString 还有另外几个简化：
- 不直接显示 "null"，而是用 "()" 代表 null。
- 如果遇到 second 不是 pair 的 pair，中间不是显示 ", "，而是显示一个点 " . "，两边有空格。
- 如果 null 出现在 second 的位置，就 null 和中间的分隔符 " . " 都不显示。

下面是 listToString 的模版和测试：
```js
function listToString(x)
{
  function convert(x, paren)
  {
    // TODO
  }
  
  return convert(x, true);
}

show("---- listToString ----");

show(listToString(null));
// ()
show(listToString(pair(2, pair(3, null))));
// (2 3)
show(listToString(pair(pair(2, 3), null)));
// ((2 . 3))
show(listToString(pair(2, pair(3, 4))));
// (2 3 . 4)
show(listToString(pair(pair(2, 3), 4)));
// ((2 . 3) . 4)
show(listToString(pair(pair(2, pair(3, null)), 4)));
// ((2 3) . 4)
show(listToString(pair(pair(2, 3), pair(4, 5))));
// ((2 . 3) 4 . 5)
```

listToString 的方式，其实就是 Lisp 语言显示链表的方式。如果有复杂的链表嵌套的时候（比如 permute 的结果），这种显示方式会比 pairToString 清晰。但如果不是链表，而是树的时候，这种显示不一定更容易理解。




# 个人总结

树基础模型图草稿图:\
![[20210411220537120_13657.png]]




