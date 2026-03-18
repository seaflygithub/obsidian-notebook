[TOC]

# 作业提交与反馈(微信多对一辅导群)

## 线性查找表
我们可以用链表来构造一种很有用的数据结构，叫做**查找表**（lookup table）。比如，餐厅的菜单就是一个查找表。每行有两个项目，菜名和价格。按左边的菜名，就能找到对应的价格。

![[20210411220943048_23646.png]]

为什么我们能找到菜名对应的价格呢？因为它们处于同一行，所以建立起一种对应关系。

我们可以用 pair 来表示这种对应关系。每行做成一个 pair，把多个行放在一个链表里。也就是说，链表里放着一系列的 pair。这种特殊结构的链表，通常叫做 association list，不过我们这里为了意义明确，就叫它**线性查找表**。

我们的线性查找表的构造函数叫 **addTable**，它有三个参数：key，value，table。其中 table 是一个已有的查找表，key 和 value 是我们想放进去的新信息。addTable 不修改原来的 table，而是返回一个新的 table，这个 table 比起原来的，多了 key 和对应的 value。

如果 table 里原来就有相同的 key，那么原来的 key-value 会被压在下面。查找的时候，只要看到 key 第一次出现就返回 value，所以就查不到旧的值了。这就相当于更新了查找表。这样一来，原来的 table 还存在，而且保留着旧的信息，新的 table 包含了更新的信息。新旧两个数据都可以用，只要能访问到它们就行。

这种不做"破坏性"修改操作数据结构，通常叫**函数式数据结构**。我们之前学过的数据结构全都是函数式数据结构，因为我们根本没有定义可以修改它们的操作。我们没有修改原来的数据，而只是生成了更大的结构，把原来的包在了里面而已。

addTable 已经给出，下面请你自己实现 **lookupTable**。
```js
// 空的查找表（起始值）
var emptyTable = null;

// 把 key-value 对加入到 table，返回新的 table
function addTable(key, value, table)
{
  return pair(pair(key, value), table);
}

function lookupTable(key, table)
{
  // TODO
  // 在 table 中查找 key 对应的 value
  // 如果找不到，返回 null
}

var menu1 = 
    addTable("pizza", 128, 
    addTable("cake", 46,
    addTable("pasta", 68,
    addTable("steak", 258,
    addTable("salad", 45,
    addTable("beer", 35, emptyTable))))));

show(pairToString(menu1));
// ((pizza, 128), ((cake, 46), ((pasta, 68), ((steak, 258), ((salad, 45), ((beer, 35), null))))))
show(lookupTable("pizza", menu1));    // 128
show(lookupTable("cake", menu1));     // 46
show(lookupTable("beer", menu1));     // 35
show(lookupTable("MSG", menu1));      // null

// 新的 menu2 给牛排降价
var menu2 = addTable("steak", 200, menu1);

show(pairToString(menu2));
// ((steak, 200), ((pizza, 128), ((cake, 46), ((pasta, 68), ((steak, 258), ((salad, 45), ((beer, 35), null)))))))
// 注意 steak 出现两次，我们只看第一个结果。

show(pairToString(menu1));
// ((pizza, 128), ((cake, 46), ((pasta, 68), ((steak, 258), ((salad, 45), ((beer, 35), null))))))
// menu1 的值并未改变

show(lookupTable("steak", menu2));
// 200。查 menu2 得到新价格
show(lookupTable("steak", menu1));
// 258。查老的 menu1 得到原来价格
```
**提示**：lookupTable 的结构比较像之前做过的 member 函数，只不过现在返回的不是 boolean，而是 key 对应的 value。


## 测试工具
我们的代码到了这个阶段，光靠肉眼来反复看测试结果已经比较累了，所以我们设计一种新的方式，可以用代码来自动检查测试是否正确。我们用程序来比较输出的结果和预想的结果，如果不一样就报错。

这种自动的「单元测试」（unit test）也是现代软件项目不可缺少的一部分。下面就是我们自己的一种简单的实现。对于每一个测试，它会自动把结果与正确的期望值进行比较，如果相等就显示 "[OK]"，否则就显示 "[FAIL]"，并且显示是哪一部分不一样。你可以先理解一下这些测试工具代码是在做什么。
```js
function testEqual(p1, p2)
{
  if (!isPair(p1) || !isPair(p2))
  {
    // 因为是测试工具，这里破例使用 === 操作符
    if (p1 === p2)
    {
      return true;
    }
    else
    {
      console.log(pairToString(p1) 
                  + " not equal to "
                  + pairToString(p2));
      return false;
    }
  }
  else
  {
    return testEqual(first(p1), first(p2))
    && testEqual(second(p1), second(p2));
  }
}

function test(name, expected, actual)
{
  if (testEqual(expected, actual))
  {
    console.log("Test '" + name + "': [OK]");
  }
  else
  {
    console.log("Test '" + name + "': [FAIL]");
  }
}
```

## 查找二叉树（BST）
线性查找表有一个问题，那就是每查找一个 key，都可能需要把整个表扫描一遍。要是有很多元素，这个过程会非常慢。我们希望有更快的办法。

思路是构造这样的一种树，每个节点里面有一个 key，所有比 key 小的节点，都在左边的分支，而所有比 key 大的节点，都在右边的分支。这个性质对每一个节点都成立。这种结构叫**查找二叉树**（binary search tree），简称 **BST**。下面是一个 BST 的例子：

![[20210411221019755_23264.png]]

比如这个例子里，我们要寻找 14。我们首先在根节点遇到 8，因为左边分支的所有 key 都小于 8，所以根本不需要看了，只需要在右边的分支去寻找 14。用这种办法，我们可以大幅度减少比较的次数，不需要跟每一个 key 去比较。

![[20210411221045363_1066.png]]

跟线性查找表一样，我们的每个 key 要匹配一个 value。找到 key 之后，我们返回对应的 value。所以每一个节点里应该有 4 个元素：key，value，left，right。对比之前计算器用的 binop 节点，它只多了一个元素。

下图是一个例子，注意它的 key 是菜的名字，value 是菜的价格。

![[20210411221112128_11601.png]]

跟计算器的 binop 类似，我们不直接用 pair 构造 bst 节点，而是使用抽象的构造函数和访问函数。节点的构造函数和访问函数已经提供给你，还提供了一个 bstString 函数，它可以比较形象地显示 BST 的内容。你只需要把头往左转 90 度，就能比较形象的看到这棵树。你可以自己用递归思路理解一下 bstString 函数的工作原理。

现在请你自己实现 **addBST** 和 **lookupBST** 函数。这两个函数的测试因为是相关的，所以请一起做完之后再一起提交。

注意，addBST 不会改变原来的 BST，而是生成新的节点。每次插入新的元素都会生成一棵新的 BST，而不会改变原来的。我们的 BST 也是一种函数式数据结构。

```js
// bst 节点构造函数
var emptyBST = null;

function bst(key, value, left, right)
{
  return pair("bst", pair(key, pair(value, pair(left, pair(right, null)))));
}

function isBST(x)
{
  return isPair(x) && first(x) == "bst";
}

function bstKey(node)
{
  return first(second(node));
}

function bstValue(node)
{
  return first(second(second(node)));
}

function bstLeft(node)
{
  return first(second(second(second(node))));
}

function bstRight(node)
{
  return first(second(second(second(second(node)))));
}

function bstString(node)
{
  function spaces(n)
  {
    if (n == 0) {
      return "";
    }
    else {
      return " " + spaces(n - 1);
    }
  }

  function convert(node, level)
  {
    if (node == emptyBST) {
      return "\n";
    }
    else {
      return convert(bstRight(node), level + 1)
              + spaces(level * 4)
              + bstKey(node) + ":" + bstValue(node)
              + convert(bstLeft(node), level + 1);
    }
  }

  return convert(node, 0);
}

function addBST(key, value, node)
{
  // 返回一个新的 BST，它含有原来 node 的信息，并且更新了 key-value 的内容。
  // 注意：
  // - key 是菜的名字，value 是菜的价格。
  // - addBST 不会改变原来的 BST，而是生成新的 BST。每次插入新的元素都会生成一棵新的 BST，而不会改变原来的。
  // - addBST 和 lookupBST 请一起完成之后再提交。
}

function lookupBST(key, node)
{
  // TODO
}

var bstMenu1 = 
  addBST("beer", 35, 
  addBST("salad", 45,
  addBST("steak", 258, 
  addBST("pasta", 68, 
  addBST("cake", 46, 
  addBST("pizza", 128, emptyBST))))));

show("------- bst --------");
show(bstString(bstMenu1));
//     steak:258
//         salad:45
// pizza:128
//         pasta:68
//     cake:46
//         beer:35
// 注意：这里的 key 是菜的名字，不是价格。valve 才是价格。

var expect1 =
  pair("bst", pair("pizza", pair(128, 
  pair(pair("bst", pair("cake", pair(46,
  pair(pair("bst", pair("beer", pair(35, 
  pair(null, pair(null, null))))),
  pair(pair("bst", pair("pasta", pair(68, 
  pair(null, pair(null, null))))), null))))), 
  pair(pair("bst", pair("steak", pair(258, 
  pair(pair("bst", pair("salad", pair(45, 
  pair(null, pair(null, null))))), 
  pair(null, null))))), null)))));

test("bst construction", expect1, bstMenu1);

var saladPrice = lookupBST("salad", bstMenu1);
show(saladPrice); // 45
test("salad price", 45, saladPrice);

var beerPrice = lookupBST("beer", bstMenu1);
show(beerPrice); // 35
test("beer price", 35, beerPrice);

var msgPrice = lookupBST("MSG", bstMenu1);
show(msgPrice); // null
test("MSG price", null, msgPrice);

var bstMenu2 = addBST("steak", 200, bstMenu1);
show(bstString(bstMenu2));
//     steak:200
//         salad:45
// pizza:128
//         pasta:68
//     cake:46
//         beer:35
// 注意 steak 价格更新了

var expect2 =
  pair("bst", pair("pizza", pair(128, 
  pair(pair("bst", pair("cake", pair(46,
  pair(pair("bst", pair("beer", pair(35, 
  pair(null, pair(null, null))))),
  pair(pair("bst", pair("pasta", pair(68, 
  pair(null, pair(null, null))))), null))))), 
  pair(pair("bst", pair("steak", pair(200, 
  pair(pair("bst", pair("salad", pair(45, 
  pair(null, pair(null, null))))), 
  pair(null, null))))), null)))));

test("bst update steak", expect2, bstMenu2);

show(bstString(bstMenu1));
//     steak:258
//         salad:45
// pizza:128
//         pasta:68
//     cake:46
//         beer:35
// 注意 bstMenu1 的 steak 还是原来的价格

test("bstMenu1 unchanged", expect1, bstMenu1);

// 查 bstMenu2 得到新价格
var newSteakPrice = lookupBST("steak", bstMenu2);
show(newSteakPrice); // 200
test("new steak price", 200, newSteakPrice);

// 查老的 bstMenu 得到旧价格
var oldSteakPrice = lookupBST("steak", bstMenu1);
show(oldSteakPrice); // 258
test("old steak price", 258, oldSteakPrice);
```

**【SeaflyWechat】**\
老师，我有问题想请教一下，就是 addBST 是否插入节点前需要找到合适的位置插入新节点？还是直接头插法插入新节点？因为这里我不确定到底是按照 key 来排序 还是按照 value 大小来排序。。。

**【计算机科学家王垠老师ian】**\
你的思维方式有点问题，递归的思路不是“找到合适的位置插入新节点”

**【计算机科学家王垠老师ian】**\
应该思考的问题是：当递归调用把节点和左边的子树放在一起，构造出一个新的左子树之后，我如何得到完整的新的 BST？

**【SeaflyWechat】**\
哦，好的好的，我把您这句话理解一下

**【SeaflyWechat】**\
![[20210411221149522_18555.png]]



**【SeaflyWechat】**\
老师，第 BST 题提交如下(优化后):
```js
function addBST(key, value, node)
{
    // 返回一个新的 BST，它含有原来 node 的信息，并且更新了 key-value 的内容。
    // 注意：
    // - key 是菜的名字，value 是菜的价格。
    // - addBST 不会改变原来的 BST，而是生成新的 BST。每次插入新的元素都会生成一棵新的 BST，而不会改变原来的。
    // - addBST 和 lookupBST 请一起完成之后再提交。
    if (node == null)
    {
        return bst(key, value, null, null);
    }
    else if (key == bstKey(node))
    {
        //更新 value 
        return bst(bstKey(node), value, bstLeft(node), bstRight(node));
    }
    else if (key < bstKey(node))
    {
        return bst(bstKey(node), bstValue(node), addBST(key, value, bstLeft(node)), bstRight(node));
        //return addBST(key, value, bstLeft(node));//仅返回子树
    }
    else if (key > bstKey(node))
    {
        return bst(bstKey(node), bstValue(node), bstLeft(node), addBST(key, value, bstRight(node)));
        //return addBST(key, value, bstRight(node));//仅返回子树
    }
}

function lookupBST(key, node)
{
    if (node == null)
    {
        return null;
    }
    else if (key == bstKey(node))
    {
        return bstValue(node);
    }
    else if (key < bstKey(node))
    {
        return lookupBST(key, bstLeft(node));
    }
    else if (key > bstKey(node))
    {
        return lookupBST(key, bstRight(node));
    }
}

```

**【SeaflyWechat】**\
老师，第 BST 题提交如下(优化后):
```js
function addBST(key, value, node)
{
    // 返回一个新的 BST，它含有原来 node 的信息，并且更新了 key-value 的内容。
    // 注意：
    // - key 是菜的名字，value 是菜的价格。
    // - addBST 不会改变原来的 BST，而是生成新的 BST。每次插入新的元素都会生成一棵新的 BST，而不会改变原来的。
    // - addBST 和 lookupBST 请一起完成之后再提交。
    if (node == null)
    {
        return bst(key, value, null, null);
    }
    else if (key == bstKey(node))
    {
        //更新 value 
        return bst(key, value, bstLeft(node), bstRight(node));
    }
    else if (key < bstKey(node))
    {
        return bst(bstKey(node), bstValue(node), addBST(key, value, bstLeft(node)), bstRight(node));
        //return addBST(key, value, bstLeft(node));//仅返回子树
    }
    else
    {
        return bst(bstKey(node), bstValue(node), bstLeft(node), addBST(key, value, bstRight(node)));
        //return addBST(key, value, bstRight(node));//仅返回子树
    }
}

function lookupBST(key, node)
{
    if (node == null)
    {
        return null;
    }
    else if (key == bstKey(node))
    {
        return bstValue(node);
    }
    else if (key < bstKey(node))
    {
        return lookupBST(key, bstLeft(node));
    }
    else
    {
        return lookupBST(key, bstRight(node));
    }
}
```




# 无垠王垠 (新浪微博)
12月7日 17:34 来自 微博 weibo.com 已编辑

计算机科学基础班进行了这么久，并不是没有失败的案例的。总的说来，大部分学生成功地掌握了重要的思维，而极少数失败的情况起初有点难以理解。经过分析，发现了这样一些规律：

1. 成功掌握课程内容，跟人的基础几乎没有关系。学生不需要良好的数学基础，不需要任何编程基础。我所要求的数学基础，是知道“2 * 3 等于 6”这样的小学数学。成功毕业的同学，有医生，律师，产品经理，水电工，印钞厂工人，卖酒的商人…… 当然，也有计算机博士已经毕业的人。只要用心基本都能学会。

2. 成功的案例都是愿意花心思在这上面的人。有极少数失败的案例，是报名之后却不愿意花心思的人。世上无难事，只怕有心人。我目前还没有方法让一个不用心的人顺利掌握课程内容。

3. 成功的，顺利的案例，往往是愿意放下已有的思维，从头开始的人。极少数失败的案例，似乎有某种封闭心理，总是试图用已有的思维方式（比如学过的数学，其它的编程概念）来“解释”我教的内容。所以有极少数的人学完了课程，却似乎没学到什么，因为他们太执着于保留自己原来的思维。

在心理上，他们把已经会的东西放在很高的地位，而没有仔细理解和吸收我教的东西。一个现象就是，他们会问我：“老师，你看我这样理解对不对？…… ” 接着是对自己思想的大段描述或者复杂的图，把我讲的东西用他自己的语言翻译了一遍，夹杂着很多其它地方学来的术语，或者自己别出心裁。为什么有人想要跟我学东西，不仔细理解和吸收我总结出来的内容，却期望我去理解他写的内容？心理上的师生关系都弄反了，又怎么学习呢？

实话说，我是看不懂这些“我的理解”的，因为那完全不是我教的东西，我也没有时间和精力去看别人大段的论述。看这些东西对于我的思维是一种干扰，所以大段的自然语言描述，我一般是不看的。

这里有一个“谁是本质”，“谁是基础”的问题。顺利的方式是用本质而基础的思想去解释不那么基础的内容或者术语，而不是反过来。你只能用简单正确的理论去解释复杂错误的理论，而不是用复杂错误的理论来解释简单正确的。


