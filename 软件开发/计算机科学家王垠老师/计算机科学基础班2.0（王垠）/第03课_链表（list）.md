[TOC]

# 课堂记录(递归与链表)

## 数据结构构造函数
```js
function pair(a, b)//构造函数
{
  return select => select(a, b);
}

var p1 = pair(2, 3);  // 创造一个新的 pair 结构，内容是 2 和 3。
var p1 = pair(2, 3);
// show(p1((a, b) => a * b));  // 会返回 6
// show(p1((a, b) => a + b));  // 会返回 5
```

## 数据结构访问函数
```js
function first(p)//访问函数
{
    return p((a, b) => a);
}

function second(p)//访问函数
{
    return p((a, b) => b);
}

var p1 = pair(2, 3);
// show(first(p1));
// show(second(p1));

// show(typeof(2));
// show(typeof("hhhh"));
// show(typeof(p1));
```

## 数据结构类型判断函数
```js
function isPair(x)
{
    return typeof(x) == "function";
}

// show(isPair(p1));
```

## 显示pair内容函数
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

show(pairToString(p1));
var p2 = pair(4, p1);
show(pairToString(p2));
```

## 依赖于抽象接口

什么叫依赖于抽象接口:就是这个函数能否正常运行，依赖于它里面调用的那些函数。
![[20210323185055321_3749.png]]


## 数据结构模型图
![[20210323185255393_11115.png]]

下面这个表达式的分析:

pair(3, 4)虽然不是一个链表, 但是它同时也在前一个pair的first位置。
链表就是有限制的pair结构。
该表达式第0个元素是2。
该表达式第1个元素是pair(3, 4)。

**我们看元素其实是看first的位置(链表节点)。**
该表达式第1个元素不存在，null表示一个链表结束了,它不是一个元素。

pair(2, pair(pair(3, 4), null))表达式模型图如下：
![[20210323185418209_27683.png]]

## 计算链表长度(即节点个数)
```js
function length(ls)
{
    if (ls == null)
    {
        return 0;
    }
    else
    {
        return (1 + length(second(ls)));
    }
}
var p2 = pair(2, pair(pair(3, 4), null));
var ls1 = pair(2, pair(3, null));
var ls2 = pair(4, pair(5, pair(6, null)));
var ls3 = pair(4, pair(pair(2, 3), pair(6, null)));
show(length(p2));
show(length(ls3));
//总结:当你知道该问题所描述的具体模型了,你离解题就不远了。
```

ls3链表模型图草稿图如下:
![[20210323185545328_14669.png]]


## 两个链表拼接起来(append)
```js
var head = first;
var tail = second;
function append(ls1, ls2)
{
    if (ls1 == null)
    {
        return ls2;
    }
    else
    {
        return pair(head(ls1), append(tail(ls1), ls2));
    }
}

show(pairToString(ls1));
show(pairToString(ls2));
show(pairToString(ls3));

show(pairToString(append(ls1, ls2)));
show(pairToString(append(ls1, ls3)));

// (2, (3, null))
// (4, (5, (6, null)))
// (4, ((2, 3), (6, null)))
// (2, (3, (4, (5, (6, null)))))
// (2, (3, (4, ((2, 3), (6, null)))))
```

append链表拼接模型图：
![[20210323185650720_26254.png]]

```js
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
show(pairToString(append(list1, list2)));
//(7, (3, (2, (9, (5, (4, (6, (1, (8, null)))))))))
```
append_list1_list2模型图:
![[20210323185822087_6274.png]]

## 链表第n个节点(nth)
```js
function nth(ls, n)
{
    if (n == 0)
    {
        if (ls != null)
        {
            return head(ls);
        }
        else
        {
            throw "out of bound"
        }
    }
    else if (ls == null)
    {
        throw "out of bound"
    }
    else
    {
        return nth(tail(ls), n - 1);
    }
}

//优化后的nth函数:
function nth(ls, n)
{
    if (ls == null)
    {
        throw "out of bound"
    }
    else if (n == 0)
    {
        return head(ls);
    }
    else
    {
        return nth(tail(ls), n - 1);
    }
}

var ls3 = pair(4, pair(pair(2, 3), pair(6, null)));
show(pairToString(nth(ls3, 0)));// 4
show(pairToString(nth(ls3, 1)));// (2, 3)
show(pairToString(nth(ls3, 2)));// 6
//4
//(2, 3)
//6
```

# 作业提交与反馈(微信多对一辅导群)

## 数据结构构造函数(pair)
```js
function pair(a, b)
{
    return f => f(a, b);
}
```

## 数据结构访问函数(first, seconde)
```js
function first(p)
{
    return p((a, b) => a);
}

function second(p)
{
    return p((a, b) => b);
}
```

## 数据结构类型判断函数(isPair)
```js
function isPair(x)
{
    return typeof(x) == "function";
}
```

## 数据结构内容展示(pairToString)
```js
function pairToString(p)
{
    if (isPair(p) == false)
    {
        return String(p);
    }
    else
    {
        return "("
        + pairToString(first(p))
        + ", "
        + pairToString(second(p))
        + ")";
    }
}
var p1 = pair(2, 3);
var p2 = pair(2, pair(3, 4));

show(pairToString(p1));//(2, 3)
show(pairToString(p2));//(2, (3, 4))
```

## 链表长度/链表节点个数(listLength)
```js
function listLength(ls)
{
    if (ls == null)
    {
        return 0;
    }
    else
    {
        return 1 + listLength(second(ls));
    }
}

var p1 = pair(2, null);
var p2 = pair(2, pair(3, null));
show(listLength(p1));//1
show(listLength(p2));//2
```

## 拼接两个链表(append)
```js
function append(ls1, ls2)
{
    if (ls1 == null)
    {
        return ls2;
    }
    else
    {
        return pair(head(ls1), append(tail(ls1),ls2));
    }
}
var ls1 = pair(2, null);
var ls2 = pair(2, pair(3, null));
show(pairToString(append(ls1, ls2)));
```

## 链表第n个节点(nthListNode)
```js
function nthListNode(ls, n)
{
    if (n == 0)
    {
        return head(ls);
    }
    else if (ls == null)
    {
        throw "out of bound"
    }
    else
    {
        return nthListNode(second(ls), n - 1);
    }
}
var ls1 = pair(2, null);
var ls2 = pair(2, pair(3, null));
var ls3 = append(ls1, ls2);
show(pairToString(ls3));//(2, (2, (3, null)))
show(pairToString(nthListNode(ls3, 0)));//2
show(pairToString(nthListNode(ls3, 1)));//2
show(pairToString(nthListNode(ls3, 2)));
```

## 链表模型图

【SeaflyWechat】
老师请问一下下面这个表达式转换成对应链表模型图是正确吗？
![[20210323203612962_11694.png]]


【计算机科学家王垠老师ian】
可以，不过我觉得应该画箭头而不是线。

【SeaflyWechat】
哦，好的，我修正过来。
![[20210323203643279_9347.png]]

## 思考题：append 产生的 pair
append 在执行过程中，总共会产生多少个新的 pair？

【SeaflyWechat】
答：append在执行过程中，总共会产生length(ls1)个新的pair。
![[20210323203748308_13989.png]]

【维加】
对的

## last
head 会返回链表的第一个元素，如何得到最后一个元素呢？写一个函数 last，它返回链表 ls 的最后一个元素。
```js
function last(ls)
{
  // 返回链表的最后一个元素
}

show("---- last -----")
show(pairToString(list1));
// (7, (3, (2, (9, null))))

show(last(list1));
// 9

show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(last(list2));
// 8

show(last(null));
// 报错"链表是空的"
```

【SeaflyWechat】
```js
var head = first;
var tail = second;
function last(ls)
{
    if (ls == null)
    {
        throw "list is empty"
    }
    else
    {
        if (tail(ls) == null)
        {
            return head(ls);
        }
        else
        {
            return last(tail(ls));
        }
    }
}
show("---- last -----");
show(pairToString(list1));// (7, (3, (2, (9, null))))
show(last(list1));// 9
show(pairToString(list2));// (5, (4, (6, (1, (8, null)))))
show(last(list2));// 8
show(last(null));// 报错"链表是空的"
```

【维加】
throw 一行少个分号；可以把第二个 if 换成 else if。

【SeaflyWechat】
哦，好的，我马上改回来
```js
var head = first;
var tail = second;
function last(ls)
{
    if (ls == null)
    {
        throw "list is empty";
    }
    else if (tail(ls) == null)
    {
        return head(ls);
    }
    else
    {
        return last(tail(ls));
    }
}
show("---- last -----");
show(pairToString(list1));// (7, (3, (2, (9, null))))
show(last(list1));// 9
show(pairToString(list2));// (5, (4, (6, (1, (8, null)))))
show(last(list2));// 8
show(last(null));// 报错"链表是空的"
```

## member
写一个函数 member，它接受两个参数 x 和 ls。它返回一个 boolean，表示 x 是否在链表 ls 里面。
```js
function member(x, ls) 
{
}

show("----- member -----");
show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(member(3, list2));    // false
show(member(4, list2));    // true
```

【SeaflyWechat】
第member题提交如下：
```js
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
// show(pairToString(append(list1, list2)));
//(7, (3, (2, (9, (5, (4, (6, (1, (8, null)))))))))

var head = first;
var tail = second;
function member(x, ls) 
{
    if (ls == null)
    {
        return false;
    }
    else if (head(ls) == x)
    {
        return true;
    }
    else
    {
        return member(x, tail(ls));
    }
}

show("----- member -----");
show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(member(3, list2));    // false
show(member(4, list2));    // true
```

【SeaflyWechat】
老师，我有个疑问:就是当前两个条件判断表达式相互交换一下位置，就过不了语法检查。代码如下：
```js
function member(x, ls) 
{
    if (head(ls) == x)
    {
        return true;
    }
    else if (ls == null)
    {
        return false;
    }
    else
    {
        return member(x, tail(ls));
    }
}
```

【计算机科学家王垠老师ian】
不是语法检查的问题，那两个条件本来就不能换位置吧。

【SeaflyWechat】
没理解，万一第一次传进去的x满足条件呢？
这种变换位置还导致结果大不一样的情况，会不会常常在实际中出现？

【维加】
不能换的，你试试 member(0, null)

【SeaflyWechat】
哦，明白了，这个极端条件我没考虑到。。

## rember
写一个函数 rember。rember 是"remove member"的意思，但它并不从原来的链表去掉元素。rember 会造出一个新的链表，这个新的链表就像把元素 x 从 ls 里去掉之后的样子。如果有重复出现，就去掉所有的。
```js
function rember(x, ls)
{
  // 从 ls 去掉所有 x
  // 注意不要使用 filter 来实现
}

show("----- rember -----");
var listRember = 
    pair(3, pair(7, pair(2, (pair(3, pair(4, pair(3, null)))))));

show(pairToString(listRember));
// (3, (7, (2, (3, (4, (3, null))))))

show(pairToString(rember(2, listRember)));
// (3, (7, (3, (4, (3, null)))))

show(pairToString(rember(4, listRember)));
// (3, (7, (2, (3, (3, null)))))

show(pairToString(rember(3, listRember)));
// (7, (2, (4, null)))
```

【计算机科学家王垠老师ian】
你好像过分依赖于你画的图了

【SeaflyWechat】
额，老师，我好像受到前面“计算图”所困了
就是解题前不得不逼自己画出个类似“计算图”的图来帮助解题 ......

【计算机科学家王垠老师ian】
而且你的图恐怕是带入了之前的没有对的思想的。你可以思考一下要写的函数对于输入是要输出什么，而不是假定画的图就是那个意思。

【计算机科学家王垠老师ian】
你的rember不应该卡很久。还在这个地方没进展吗？

【SeaflyWechat】
是的，老师，我把前面的题重做了个遍，找思路。可能是最近工作压力大了点影响我思路了。没事的老师，让我先再琢磨一两天。

```js
//以下表达式用来展示 head 和 tail 到底用来做了什么
show("Show part of list:");
var listRember = pair(3, pair(7, pair(2, (pair(3, pair(4, pair(3, null)))))));
show(pairToString(head(listRember)));//3
show(pairToString(head(tail(listRember))));//7
show(pairToString(head(tail(tail(listRember)))));//2
show(pairToString(listRember));//(3, (7, (2, (3, (4, (3, null))))))
show(pairToString(tail(listRember)));//(7, (2, (3, (4, (3, null)))))
show(pairToString(tail(tail(listRember))));//(2, (3, (4, (3, null))))

//从上述表达式的执行结果分析出来
//head 这个访问接口的功能就做了一件事，就是取出pair的首部并返回，即只有一个数字。
//tail 这个访问接口的功能就是返回 pair 的 后半部分，在这里表现出把链表后半部分全部展示出来了。
//基于上两条总结, 整个 pair 链表本身表现为一种递归式的链表特征。
//也就是 pair 链表本身表现为不是那种我们前面常见的 一个一个节点相互连接。
//而是 一个 顶层 pair 包含 head 和 tail, tail 就是整个链表的后半部分。
```

【计算机科学家王垠老师ian】
递归函数的思想，一个要点在于从要定义的函数的“意义”去思考。也就是说去思考如果你给它一个输入，它应该给你什么输出。

【SeaflyWechat】
rember作业提交如下：
```js
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
var listRember = pair(3, pair(7, pair(2, (pair(3, pair(4, pair(3, null)))))));
var listRember = pair(4, pair(3, pair(3, pair(7, pair(3, null)))));
function rember(x, ls)
{
  // 从 ls 去掉所有 x
  // 注意不要使用 filter 来实现
  if (ls == null)
  {
    return null;
  }
  else
  {
    if (head(ls) == x)
    {
        return rember(x, tail(ls));
    }
    else
    {
        return pair(head(ls), rember(x, tail(ls)));
    }
  }
}
show(pairToString(listRember));
show(pairToString(rember(3, listRember)));
show(pairToString(listRember));
```

【计算机科学家王垠老师ian】
对的

【计算机科学家王垠老师ian】
你别沉迷于画图了。

【SeaflyWechat】
额，好的，老师

【SeaflyWechat】
老师，我是反复看了您这段话，然后直接想象直接代值进去，让rember输出我想要的结果。

## take
写一个函数 take，它接受两个参数 ls 和 n，它取得链表 ls 的前 n 个元素，把它们放在一个新的链表里返回。如果 n 超过了 ls 的长度就报错。

注意，你的函数不可以用基本的 pair，head，tail 之外的复杂函数。比如你不能用 length，nth 或者 append。
```js
function take(ls, n)
{
  // 得到 ls 的前 n 个元素，把它们放在一个 list 里返回
}

// 示例
show("----- take -----")
show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(take(list2, 0)));
// null

show(pairToString(take(list2, 3)));
// (5, (4, (6, null)))

show(pairToString(take(list2, 5)));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(take(list2, 9)));
// 报错：超出链表长度
```

【SeaflyWechat】
```js
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
function take(ls, n)
{
  // 得到 ls 的前 n 个元素，把它们放在一个 list 里返回
    if (n == 0)
    {
        return null;
    }
    else
    {
        if (ls == null)
        {
            throw "out of bound"
        }
        else
        {
            return pair(head(ls), take(tail(ls), n - 1));
        }
    }
}

// 示例
show("----- take -----")
show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(take(list2, 0)));
// null

show(pairToString(take(list2, 3)));
// (5, (4, (6, null)))

show(pairToString(take(list2, 5)));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(take(list2, 9)));
// 报错：超出链表长度
```

【计算机科学家王垠老师ian】
可以用 else if 的写法，你好像还一直没用那个。

【SeaflyWechat】
额，好的，我改一下。
```js
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
function take(ls, n)
{
  // 得到 ls 的前 n 个元素，把它们放在一个 list 里返回
    if (n == 0)
    {
        return null;
    }
    else if (ls == null)
    {
        throw "out of bound";
    }
    else
    {
        return pair(head(ls), take(tail(ls), n - 1));
    }
}
```

## drop
写一个函数 drop，它接受两个参数 ls 和 n，返回一个链表。返回的链表相当于 ls 去掉了前 n 个元素。如果 n 超过了 ls 的长度就报错。这个函数不改变原来的链表。
```js
function drop(ls, n)
{
  // 返回一个新的链表，它"去掉"了 ls 的前 n 个元素
}

show("---- drop -----")
show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(drop(list2, 0)));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(drop(list2, 2)));
// (6, (1, (8, null)))

show(pairToString(drop(list2, 3)));
// (1, (8, null))

show(pairToString(drop(list2, 5)));
// null

show(pairToString(drop(list2, 9)));
// 报错：超出链表长度
```

【SeaflyWechat】
```js
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
function drop(ls, n)
{
  // 返回一个新的链表，它"去掉"了 ls 的前 n 个元素
  if (n == 0)
  {
      return ls;
  }
  else if (ls == null)
  {
      throw "out of bound";
  }
  else
  {
      return drop(tail(ls), n - 1);
  }
}
```

## remove
写一个函数 remove，它接受两个参数 ls 和 n，它去掉链表 ls 的第 n 个元素，把剩下的元素放在一个新的链表里返回。如果 n 超过了 ls 的最大下标就报错。
```js
function remove(ls, n)
{
  // 去掉链表的第 n 个元素
}

// 示例
show("---- remove -----")
show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(remove(list2, 0)));
// (4, (6, (1, (8, null))))

show(pairToString(remove(list2, 2)));
// (5, (4, (1, (8, null))))

show(pairToString(remove(list2, 9)));
// 报错

show(pairToString(remove(null, 0)));
// 报错
```

【SeaflyWechat】
第remove题提交：
```js
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
function remove(ls, n)
{
  // 去掉链表的第 n 个元素
  if (n == 0)
  {
      return tail(ls);
  }
  else if (ls == null)
  {
      throw "out of bound";
  }
  else
  {
      return pair(head(ls), remove(tail(ls), n - 1));
  }
}
```

## map
写一个函数 map，它接受一个函数 f 和一个链表 ls。它把 f 作用于 ls 的每一个元素，把它们的结果按顺序组成一个新的链表返回。
```js
function map(f, ls)
{
  // 把 f 作用于 ls 的每一个元素
}

show("----- map -----")
show(pairToString(map(x => x * x, list2)));
// (25, (16, (36, (1, (64, null)))))

show(pairToString(map(x => x > 5, list2)));
// (false, (false, (true, (false, (true, null)))))
```

【SeaflyWechat】
第 map 题提交：
```js
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
function map(f, ls)
{
  // 把 f 作用于 ls 的每一个元素
  if (ls == null)
  {
      return null;
  }
  else
  {
      return pair(f(head(ls)), map(f, tail(ls)));
  }
}
```

## filter
写一个函数 filter（过滤器）。它接受两个参数 pred 和 ls。其中 pred 是一个返回 boolean 的函数，它表示元素是否符合条件。filter 会去掉链表 ls 里不满足 pred 的元素，把满足 pred 条件的元素放在一个新的链表里返回。
```js
function filter(pred, ls)
{
  // 返回一个新链表，只包含满足 pred 函数条件的元素
}

// 示例
show("---- filter -----")
show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(filter(x => x % 2 == 1, list2)));
// % 表示"求余数"，所以除以 2 余 1 表示"奇数"
// (5, (1, null))

show(pairToString(filter(x => x % 3 == 0, list2)));
// 3 的倍数
// (6, null)

show(pairToString(filter(x => x > 4, list2)));
// (5, (6, (8, null)))
```

【SeaflyWechat】
第 filter 题提交：
```js
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
function filter(pred, ls)
{
  // 返回一个新链表，只包含满足 pred 函数条件的元素
  if (ls == null)
  {
      return null;
  }
  else if (pred(head(ls)))
  {
      return pair(head(ls), filter(pred, tail(ls)));
  }
  else
  {
      return filter(pred, tail(ls));
  }
}
```

## zip
写一个函数 zip，它接受两个链表 ls1 和 ls2，把它们对应的元素组成一个 pair，返回一个这些 pair 按顺序组成的链表。zip 的意思是“拉链”，想象一下拉链的两边被拉在一起的时候的样子。如果其中一个链表比另一个长，只返回短链表那么长的「拉链链表」。
![[20210323204636774_3920.png]]
```js
function zip(ls1, ls2)
{
  // TODO
}

show("----- zip -----")
show(pairToString(list1));
// (7, (3, (2, (9, null))))

show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(zip(list1, list2)));
// ((7, 5), ((3, 4), ((2, 6), ((9, 1), null))))
```

【SeaflyWechat】
第 zip 题提交：
```js
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
function zip(ls1, ls2)
{
  // TODO
  if (ls1 == null || ls2 == null)
  {
      return null;
  }
  else
  {
      return pair(pair(head(ls1), head(ls2)), zip(tail(ls1), tail(ls2)));
  }
}
```

## listEqual
写一个函数 listEqual, 它能告诉我们两个链表的内容是否完全相同。我们不能用 == 直接比较两个链表是否相等，因为 == 只能比较两个简单的数据，比如数字。对于复杂的数据结构，== 只能比较它们是否是「同一份数据」。所以 == 可以比较两个指向链表的变量是否同一个链表，但不会递归进行深层次的「值比较」。我们只有自己写一个递归函数来进行这种深层比较。
```js
function listEqual(ls1, ls2)
{
  // TODO
}

var listC1 = pair(7, pair(3, pair(2, pair(9, null))));
var listC2 = pair(7, pair(3, pair(2, pair(9, pair(10, null)))));

var listC3 = pair(7, pair(3, null));
var listC4 = pair(2, pair(9, null));

show(listEqual(list1, list2));
// false
show(listEqual(list1, list1));
// true
show(listEqual(list1, listC1));
// true
show(listEqual(list1, listC2));
// false
show(listEqual(listC2, listC1));
// false
show(listEqual(list1, append(listC3, listC4)));
// true
show(listEqual(pair(0, list1), pair(0, listC1)));
// true
show(listEqual(pair(0, listC1), pair(1, listC1)));
// false
```

提示：你可能发现这个函数里的逻辑条件可以用 && 或者 || 之类的逻辑操作符组合起来。其中有一些是清晰的就可以组合，但是建议不要利用 && 或 || 的所谓"短路特性"，把本来有先后顺序的表达式连接在一起。这种写法看似聪明，但却很容易误解或忽视里面隐含的先后顺序。

【SeaflyWechat】
第 listEqual 题提交：
```js
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
function listEqual(ls1, ls2)
{
    if (ls1 == null)
    {
        if (ls2 == null)
        {
            return true;
        }
        else
        {
            return false;
        }
    }
    else
    {
        if (ls2 == null)
        {
            return false;
        }
        else
        {
            if (head(ls1) != head(ls2))
            {
                return false;
            }
            else
            {
                return listEqual(tail(ls1), tail(ls2));
            }
        }
    }
}
```

【Super喵喵玄】
可以简化一下，其他的改成 else if 写。其实 ls2 == null 和 ls1 == null 是相似的 base case。直接返回 ls2 == null。

【SeaflyWechat】
好的，第 listEqual 题简化后提交：
```js
function listEqual(ls1, ls2)
{
    if (ls1 == null)
    {
        return ls2 == null;
    }
    else if (ls2 == null)
    {
        return false;
    }
    else
    {
        if (head(ls1) != head(ls2))
        {
            return false;
        }
        else
        {
            return listEqual(tail(ls1), tail(ls2));
        }
    }
}
```

## reverse
写一个函数 reverse，它会反转一个链表。reverse 返回一个新的链表，正好是 ls 的元素反过来。你的实现可以用 append，但不要用其它函数。
```js
function reverse(ls)
{
  // 返回一个新的链表，正好是 ls 的元素反过来。
}

// 示例
show("----- reverse -----");
show(pairToString(list1));
// (7, (3, (2, (9, null))))

show(pairToString(reverse(list1)));
// (9, (2, (3, (7, null))))

show(pairToString(list2));
// (5, (4, (6, (1, (8, null)))))

show(pairToString(reverse(list2)));
// (8, (1, (6, (4, (5, null)))))
```

【SeaflyWechat】
好的，第 reverse 题提交：
```js
var show = console.log;
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));

function reverse(ls)
{
    // 返回一个新的链表，正好是 ls 的元素反过来。
    if (ls == null)
    {
        return null;
    }
    else
    {
        return append(reverse(tail(ls)), pair(head(ls), null));
    }
}

var list1 = pair(3, null);
var list2 = pair(3, pair(4, null));
var list3 = pair(3, pair(4, pair(5, null)));

show(pairToString(reverse(list1)));
show(pairToString(reverse(list2)));
show(pairToString(reverse(list3)));
```

【Super喵喵玄】
对的。

## sum
写一个函数 sum，它把输入的链表里的所有数字加在一起。你可以假设输入的链表里都是数字。
```js
function sum(ls)
{
  // TODO
}

show("---- sum ----");
show(sum(list1));  // 21
show(sum(list2));  // 24
show(sum(null));   // 0
```

【SeaflyWechat】
老师，第 sum 题提交如下：
```js
function sum(ls)
{
    if (ls == null)
    {
        return 0;
    }
    else
    {
        return head(ls) + sum(tail(ls));
    }
}

show("---- sum ----");
show(sum(list1));  // 21
show(sum(list2));  // 24
show(sum(null));   // 0
```

## prod
写一个函数 prod，它把输入的链表里的所有数字乘在一起。你可以假设输入的链表里都是数字。
```js
function prod(ls)
{
  // TODO
}

show("---- prod ----");
show(prod(list1));  // 378
show(prod(list2));  // 960
show(prod(null));   // 1
```

【SeaflyWechat】
老师，第 prod 题提交如下：
```js
function prod(ls)
{
    if (ls == null)
    {
        return 1;
    }
    else
    {
        return head(ls) * prod(tail(ls));
    }
}

```

## minimum
写一个函数 minimum，它返回非空链表里最小的一个数。
```js
function minimum(ls)
{
  // 返回非空链表里最小的一个数
}

show("----- minimum -----");
show(minimum(list1));    // 2
show(minimum(list2));    // 1
```

提示：你可以先写一个帮助函数叫 min，它返回两个参数 a 和 b 里面较小的一个。

【SeaflyWechat】
老师，第 minimum 题提交如下：
```js
function minimum(ls)
{
    // 返回非空链表里最小的一个数
    if (ls == null)
    {
        return 0;
    }
    else if (tail(ls) == null)
    {
        return head(ls);
    }
    else
    {
        return head(ls) < head(tail(ls)) ?
                minimum(pair(head(ls), tail(tail(ls))))
                :
                minimum(pair(head(tail(ls)), tail(tail(ls))));
    }
}
```

【SeaflyWechat】
老师，第 minimum 题通过 min 简化后提交如下：
```js
function min(numa, numb)
{
    return numa < numb ? numa : numb;
}

function minimum(ls)
{
    // 返回非空链表里最小的一个数
    if (ls == null)
    {
        return 0;
    }
    else if (tail(ls) == null)
    {
        return head(ls);
    }
    else
    {
        return  minimum(pair(min(head(ls), head(tail(ls))), tail(tail(ls))));
    }
}
```

## maximum
写一个函数 maximum，它返回非空链表里最大的一个数。
```js
function maximum(ls)
{
  // 返回非空链表里最大的一个数
}

show("----- maximum -----");
show(maximum(list1));    // 9
show(maximum(list2));    // 8
```

提示：你可以先写一个帮助函数叫 max，它返回两个参数 a 和 b 里面较大的一个。

【SeaflyWechat】
老师，第 maximum 题提交如下：
```js
function max(numa, numb)
{
    return numa > numb ? numa : numb;
}

function maximum(ls)
{
    // 返回非空链表里最大的一个数
    if (ls == null)
    {
        return 0;
    }
    else if (tail(ls) == null)
    {
        return head(ls);
    }
    else
    {
        return  maximum(pair(max(head(ls), head(tail(ls))), tail(tail(ls))));
    }
}

show("----- maximum -----");
show(maximum(list1));    // 9
show(maximum(list2));    // 8
```

【计算机科学家王垠老师ian】
这两个函数写得不大好。你想想自然的递归调用要怎么写。

【计算机科学家王垠老师ian】
另外，这个题不需要考虑输入 null 的情况。

【计算机科学家王垠老师ian】
我之前的例子，每一个讲的时候都说了递归调用是怎么写，首先要想到的写法。

【SeaflyWechat】
哦，好的老师，我再看看改改。

【SeaflyWechat】
老师，您看改成这样行吗？ 从可读性应该比上一回要友好一些。
```js
function max(numa, numb)
{
    return numa > numb ? numa : numb;
}

function maximum(ls)
{
    // 返回非空链表里最大的一个数
    if (tail(ls) == null)
    {
        return head(ls);
    }
    else
    {
        var maxValue = max(head(ls), head(tail(ls)));
        var listNext = pair(maxValue, tail(tail(ls)));
        return maximum(listNext);
    }
}
```

【计算机科学家王垠老师ian】
你只是用了变量，本质没有变。

【计算机科学家王垠老师ian】
你想想，之前的链表函数，递归调用参数都是 tail(ls)

【计算机科学家王垠老师ian】
为什么你觉得 minimum 会不一样呢？

【SeaflyWechat】
老师不好意思，这两天我工作上比较忙，所以作业进度可能会比较慢。

【SeaflyWechat】
老师，自然的递归调用提交如下所示。
```js
var show = console.log;
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));

function max(numa, numb)
{
    return numa > numb ? numa : numb;
}

function maximum(ls)
{
    // 返回非空链表里最大的一个数
    if (tail(ls) == null)
    {
        return head(ls);
    }
    else
    {
        return max(max(head(ls), head(tail(ls))), maximum(tail(ls)));
    }
}
```

【SeaflyWechat】
哦？还能简化？好的，我再想想
```js
var show = console.log;
var head = first;
var tail = second;
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));

function max(numa, numb)
{
    return numa > numb ? numa : numb;
}

function maximum(ls)
{
    // 返回非空链表里最大的一个数
    if (tail(ls) == null)
    {
        return head(ls);
    }
    else
    {
        return max(head(ls), maximum(tail(ls)));
    }
}
```

## fold
写一个函数 fold。它提取出 sum 和 prod 的共同点，把不同点作为参数传进去，这样 fold 可以表示 sum 和 prod 的语义。它的工作原理类似第二课的 accum，只不过它的输入是一个链表的数字。
```js
function fold(ls, unit, combine)
{
  // TODO
}

show(fold(list1, 0, (x, y) => x + y));  // 21, 相当于 sum(list1)
show(fold(list1, 1, (x, y) => x * y));  // 378，相当于 prod(list1)
```

【SeaflyWechat】
第 fold 题提交如下：
```js
function fold(ls, unit, combine)
{
    if (ls == null)
    {
        return unit;
    }
    else
    {
        return combine(head(ls), fold(tail(ls), unit, combine));
    }
}
```

## 用 fold 重新定义一些链表函数
有了 fold，我们可以把 sum 重新定义为 sum2，把 prod 定义为 prod2：
```js
function sum2(ls)
{
  return fold(ls, 0, (x, y) => x + y);
}

function prod2(ls)
{
  return fold(ls, 1, (x, y) => x * y);
}
```

现在请你用 fold 重新定义 length，叫做 length2。

用 fold 重新定义 append，叫做 append2。

用 fold 重新定义 map，叫做 map2。

然后是 minimum，reverse……

试试用 fold 重新定义这一课写过的其它函数。哪些可以方便的被重写，哪些不那么方便？你能总结出一些规律吗？

## 重新定义 pair（用 JavaScript 对象）
之前我们说过，pair 的定义是一种抽象数据类型。我们可以改变它的 4 个抽象接口函数，完全改变 pair 的实现方式，使用 pair 的代码却完全不需要修改就能正确执行。现在我们来做一个实验，就是把 pair 的定义换掉。

我们用 JavaScript 的"对象"（object）来做这个实验。JavaScript 的对象是一种通用的数据结构表达方式，对象里面是一些有名字的「成员」。比如：
```js
var person1 =
{
  name: "James",
  sex: "male",
  age: 37,
  height: 178,
  eyeColor: "blue"
}
```

花括号里面是一些「成员」，用逗号隔开。每个成员都有名字和值，名字和值之间用冒号隔开。你可以用"点号"方式来访问对象里的成员，比如：
```js
show(person1.name);
// "James"
show(person1.height);
// 178
```

几乎所有其它语言都有类似的构造，有些语言把它叫做"类"（class）。

这样我们就能用 JavaScript 对象来改写 pair 的 4 个抽象接口了。为了避免混淆，你可以把原来的函数改名字，或者把里面的内容注释掉，然后写上新的内容。

为了避免与其它 JavaScript 对象混淆，我们在用来表示 pair 的对象里加上一个特别的成员，叫做"type"。type 对于 pair 的值就是字符串"pair"。这个特殊的成员可以用来帮助我们从其它对象中区别出我们的对象来。

pair 的构造函数已经提供给你。你只需要补充其它接口函数。完成之后，请重新运行之前的所有测试，它们全都应该正确运行，而不需要修改相关的代码。
```js
function pair(a, b)
{
  // return select => select(a, b);
  return {
    type: "pair",
    first: a,
    second: b,
  }
}

function first(p)
{
  // return p((x, y) => x);
  // 请改写
}

function second(p)
{
  // return p((x, y) => y);
  // 请改写
}

function isPair(x)
{
  // return typeof(x) == "function";
  // 请改写
}
```

提示：可以用 typeof(x) == "object" 来判断一个数据是否是 JavaScript 对象，但是 typeof(null) 也是 "object"。你需要仔细思考 isPair 应该如何准确地判断一个数据是否我们定义的 pair。

## 重新定义 pair（用数组）
这个练习里，请你用 JavaScript 的"数组"（array）来重新定义 pair。数组是一种可以用数字"下标"（subscript）访问的数据结构。你可以把它想象成一排连在一起的房间，就像酒店里的房间。每个房间有一个编号，从 0 开始依次叫 0, 1, 2, 3, ...

你可以用 [2, 3] 这样的形式来构造一个数组，然后可以用 a[0]，a[1] 这样的"下标"来访问里面的成员。比如：
```js
var a = [2, 3];
show(a[0]);  // 2
show(a[1]);  // 3
```
现在请用数组来重新实现 pair 的 4 个抽象接口。修改之后重新运行之前的所有代码，它们都应该正确运行而不需要修改。构造函数和类型判断函数应该模仿上个练习里对象的方法，具有比较准确的 type 信息。

注意：不要误解这个练习的意思。我们不是要把原来的链表「转换」成 JavaScript 的数组，他而只是用数组的方式来「实现」pair。就跟上个练习用对象来实现 pair 类似。

## permute（难）
这个练习比较难，如果一时写不出来请不要焦虑，它不会影响接下来的课程。写一个函数 permute，它列举出一个链表里元素的所有"排列"。比如：

1 只有一种排列：1。

12 有种排列：12, 21。

123 有六种排列：123, 132, 213, 231, 312, 321。

每个排列是一个链表，把所有排列放在一个链表里，也就是一个链表的链表。请注意链表的结构。
```js
function permute(ls)
{
  // TODO
}
// 示例
show(pairToString(permute(null)));
// (null, null)
show(pairToString(permute(pair(1, null))));
// ((1, null), null)
show(pairToString(permute(pair(1, pair(2, null)))));
// ((1, (2, null)),
//  ((2, (1, null)),
//   null))
show(pairToString(permute(pair(1, pair(2, pair(3, null))))));
// ((1, (2, (3, null))),
//  ((1, (3, (2, null))),
//   ((2, (1, (3, null))),
//    ((2, (3, (1, null))),
//     ((3, (1, (2, null))),
//      ((3, (2, (1, null))),
//       null))
```

提示：允许使用之前定义的函数：map, append, fold, rember。使用递归的思路，不要想“改变”或者“移动”。permute 函数大小不应该超过 20 行，如果太长很可能思路不对。

思路：拿出一个元素，把剩下的元素递归排列了，然后把这个元素放在前面。每个元素有一次在最前面的机会。

## 疑问积累
问：在作业提交过程中，代码中为什么不要用yoda notation？
答：

问：a && b；改成 if (a) { b; };什么时候用&&，什么时候用if这种？
答：表达式中没有递归，也没有什么很复杂的操作时，就可以用&&。

我觉得这个例子还有另一个因素，就是尽量不要把递归调用放在if的判断条件里面，是这样吗？
答：尽量不要用到逻辑操作里。

我明白了，就是说null依然可用，只是它不应该属于所有类型。如果null属于所有类型，那么每一个类型的对象都需要处理null这个特殊值，对吧？

## 计算机科学基础班2.0
【计算机科学家王垠老师ian】
发现好几个同学对题目里的“新的链表”感到疑惑。其实这并不是要你一定构造新的链表的意思，而只是说“不要试图去改变原来的链表”。我已经改了一下表达方式，可以刷新一下。

【计算机科学家王垠老师ian】
统一说一下一个问题。在练习中，first，second，head，tail 这类访问函数的调用，不需要考虑消除重复计算，因为这种访问函数的开销几乎可以忽略。

【计算机科学家王垠老师ian】
统一说一下另一个地方，因为出现比较多，需要简化。就是 if (x == y) { return true; } else { return false; } 这种形式，其实就等价于 return x == y;

【计算机科学家王垠老师ian】
另一个情况是有同学这样写：if (ls == null) { return ls; } else {...} 。这个情况最好是返回 null 而不是 ls。因为看到 ls 还可能以为不是 null，还得推理才知道 ls 是 null。直接写 return null 就不需要推理了。

【计算机科学家王垠老师ian】
今天的信息回复量比较大，助教们和我决定还是要固定一些时间段来回复练习。不然晚上虽然消息免打扰，看到还是忍不住要回的。今天可能就先到这里吧。明天白天再继续发吧。助教和我会商量一下怎么安排时间。

