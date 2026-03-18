[TOC]

# 作业提交与反馈(微信多对一辅导群)

## 二元操作（binop）

我们可以用树结构来实现一些更有趣的结构，比如算术表达式。因为这种算术表达式操作的都是两个数字，我们把它叫做「**二元操作**」(binary operation，**binop**)。比如：

- 2 * 3
- 1 + 2 * 3
- (1 + 2) * 3

每个二元操作（binop）包括一个「**操作符**」（比如 +, -, *, /）和两个「**操作数**」，总共 3 部分。其中两个操作数的位置都可以是另一个 binop，这样 binop 就可以嵌套。我们可以用树结构来表示 binop。

我们需要把一个操作符，两个操作数，这 3 个东西放进一种结构，然后我们需要有办法把它们取出来。至于这个结构具体是什么样子，对于使用它的代码是无关紧要的，只要放进去的东西能原封不动取出来就好。

我们需要定义 binop 的**构造函数**，**访问函数**，**类型判断函数**。构造函数叫 binop，访问函数分别叫 getOp, getE1 和 getE2。它们分别表示“得到操作符”，“得到第一个操作数”，“得到第二个操作数”。类型判断函数叫 isBinOP。

这些函数之间需要满足的合同是这样：如果 v 是 binop(op, e1, e2) 构造出来的值，那么 getOp(v) 是 op，getE1(v) 是 e1，getE2(v) 是 e2。仅当 x 是 binop 构造出来的值的时候，isBinOP(x) 是 true，否则就是 false。

下面给出一种用链表实现 binop 的方式，请补充 getOp, getE1, getE2, isBinOP 的实现。注意，这次我们在结构里放进了一个类型信息，以方便跟其它链表区别开来。

```js
function binop(op, e1, e2)
{
  return pair("binop", pair(op, pair(e1, pair(e2, null))));
}

function getOp(exp)
{
  // TODO
}

function getE1(exp)
{
  // TODO
}

function getE2(exp)
{
  // TODO
}

function isBinOP(x)
{
  // TODO
}

// 2 * 3 表示为
var exp1 = binop("*", 2, 3);
// 1 + 2 * 3 表示为
var exp2 = binop("+", 1, binop("*", 2, 3));
// (1 + 2) * 3 表示为 
var exp3 = binop("*", binop("+", 1, 2), 3);

show("----- binop -----")
show(pairToString(exp1));
// (binop, (*, (2, (3, null))))
show(getOp(exp1));
// *
show(pairToString(getE1(exp1)));
// 2
show(pairToString(getE2(exp1)));
// 3

show(pairToString(exp2));
// (binop, (+, (1, ((binop, (*, (2, (3, null)))), null)))
show(getOp(exp2));
// +
show(pairToString(getE1(exp2)));
// 1
show(pairToString(getE2(exp2)));
// (binop, (*, (2, (3, null))))

show(pairToString(exp3));
// (binop, (*, ((binop, (+, (1, (2, null)))), (3, null))))
show(getOp(exp3));
// *
show(pairToString(getE1(exp3)));
// (binop, (+, (1, (2, null)))
show(pairToString(getE2(exp3)));
// 3
```

**【SeaflyWechat】**\
老师，我有个问题想请教一下，请问下面图是我对binop的理解，这样理解是否合理？对后面作业中解决作业中问题有帮助吗？或者说这样理解反而不利于后面作业的解题？应该尽早放弃这种理解方式？

关于binop具象化的原理图_基于pair:\
![[20210411220715189_16884.png]]



**【SeaflyWechat】**\
老师，第 getOp、getE1、getE2、isBinOP 题提交如下：
```js
function binop(op, e1, e2)
{
  return pair("binop", pair(op, pair(e1, pair(e2, null))));
}

function getOp(exp)
{
    if (exp == null)
    {
        return null;
    }
    else
    {
        return left(second(exp));
    }
}

function getE1(exp)
{
    if (exp == null)
    {
        return null;
    }
    else
    {
        return left(right(second(exp)));
    }
}

function getE2(exp)
{
    if (exp == null)
    {
        return null;
    }
    else
    {
        return left(right(right(second(exp))));
    }
}

function isBinOP(x)
{
    if (x == null)
    {
        return false;
    }
    else if (isPair(x))
    {
        return (first(x) == "binop");
    }
    else
    {
        return false;
    }
}

var exp1 = binop("*", 2, 3);// 2 * 3
var exp2 = binop("+", 1, binop("*", 2, 3));// 1 + 2 * 3
var exp3 = binop("*", binop("+", 1, 2), 3);// (1 + 2) * 3

```

**【维加】**\
isBinOP 这个函数只需要判断 isPair(x) 和 first(x) == "binop" 就行了。

**【SeaflyWechat】**\
哦，好的，我改改
```js
function isBinOP(x)
{
    if (isPair(x))
    {
        return (first(x) == "binop");
    }
    else
    {
        return false;
    }
}
```

**【维加】**\
这里可以用 && 写的更简明一些。

**【SeaflyWechat】**\
好的，我好像发现了可以再简化：
```js
function isBinOP(x)
{
    return isPair(x) && (first(x) == "binop");
}
```



## toInfix
直接用 pairToString 打印出来不大好看。我们写一个函数 **toInfix**，它能把 exp1 和 exp2 这样的表达式结构转换成「中缀表达式」（infix notation），也就是普通数学表达式的形式。为了避免算术优先级的问题，我们把两边都加上括号。
```js
function toInfix(exp)
{
  // TODO
}

show("----- toInfix -----");
show(toInfix(exp1));
// (2 * 3)
show(toInfix(exp2));
// (1 + (2 * 3))
show(toInfix(exp3));
// ((1 + 2) * 3)
```


**【SeaflyWechat】**\
老师，第 toInfix 题提交如下：
```js
function toInfix(exp)
{
    if (! isBinOP(exp))
    {
        return String(exp);
    }
    else
    {
        return "("
            + toInfix(getE1(exp))
            + " "
            + getOp(exp)
            + " "
            + toInfix(getE2(exp))
            + ")";
    }
}

```

**【SeaflyWechat】**\

**【SeaflyWechat】**\




## toPrefix
写一个函数 **toPrefix**，它能把 exp1 和 exp2 这样的表达式结构转换成「前缀表达式」（prefix notation)。前缀表达式的意思是，把操作符放在最前面，而操作数放在它后面。我们也是用括号完全括起来，避免使用优先级。
```js
function toPrefix(exp)
{
  // TODO
}

show("----- toPrefix -----");
show(toPrefix(exp1));
// (* 2 3)
show(toPrefix(exp2));
// (+ 1 (* 2 3))
show(toPrefix(exp3));
// (* (+ 1 2) 3)
```

这种前缀表达式其实就是 Lisp 语言的设计。在 Lisp 语言里，所有的表达式都在一对括号中间，操作符都在括号里最前面的位置，操作数依次排在后面。比如：

- (* 2 3)
- (+ 1 (* 2 3))
- (square 3)
- (map f (list 1 2 3 4))

前缀表达式使得算术操作和函数调用的语法统一起来。观察以上 Lisp 表达式，你会发现第一个位置都是操作符。这里的"操作符"同时包括了算术操作 + - * /，也包括其它名字的函数 square, map, ...



**【SeaflyWechat】**\
老师，第 toPrefix 题提交如下：
```js
var exp1 = binop("*", 2, 3);// 2 * 3
var exp2 = binop("+", 1, binop("*", 2, 3));// 1 + 2 * 3
var exp3 = binop("*", binop("+", 1, 2), 3);// (1 + 2) * 3

function toPrefix(exp)
{
    if (! isBinOP(exp))
    {
        return String(exp);
    }
    else
    {
        return "("
            + getOp(exp)
            + " "
            + toPrefix(getE1(exp))
            + " "
            + toPrefix(getE2(exp))
            + ")";
    }
}
```

**【SeaflyWechat】**\

**【SeaflyWechat】**\






## calc

写一个函数 calc，它是一个计算器（calculator）。输入是一个 binop，输出是这个 binop 经过计算的值。

calc 很像之前写过的 sumTree，只不过它不是把树里的数都加起来，而是根据中间节点的操作符（+, -, *, /）分别进行不同的操作，所以它能计算各种各样的算术表达式。我们的计算器支持加、减、乘、除四种操作。对于其它操作符均报错，说“不支持的操作”。
```js
function calc(exp)
{
  // TODO
}

show("----- calc -----");
show(toInfix(exp1) + " = " + calc(exp1));
// (2 * 3) = 6
show(toInfix(exp2) + " = " + calc(exp2));
// (1 + (2 * 3)) = 7
show(toInfix(exp3) + " = " + calc(exp3));
// ((1 + 2) * 3) = 9

var exp4 = binop("+", binop("*", 3, 3), binop("*", 4, 4));
show(toInfix(exp4) + " = " + calc(exp4));
// ((3 * 3) + (4 * 4)) = 25

var expError = binop("$", 2, 3);
show(calc(expError));    // 报错：不支持的操作 $
```

**【SeaflyWechat】**\
老师，第 calc 题提交如下：
```js

var exp1 = binop("*", 2, 3);// 2 * 3
var exp2 = binop("+", 1, binop("*", 2, 3));// 1 + 2 * 3
var exp3 = binop("*", binop("+", 1, 2), 3);// (1 + 2) * 3

function calculator(strOp, num1, num2)
{
    if (strOp == "+")
    {
        return num1 + num2;
    }
    else if (strOp == "-")
    {
        return num1 - num2;
    }
    else if (strOp == "*")
    {
        return num1 * num2;
    }
    else if (strOp == "/")
    {
        return num1 / num2;
    }
    else
    {
        throw "报错：不支持的操作 " + strOp;
    }
}

function calc(exp)
{
    if (! isBinOP(exp))
    {
        if (! isPair(exp))
        {
            return exp;
        }
        else
        {
            return first(exp);
        }
    }
    else
    {
        return calculator(calc(getOp(exp)), calc(getE1(exp)), calc(getE2(exp)));
    }

}

show("----- calc -----");
show(toInfix(exp1) + " = " + calc(exp1));// (2 * 3) = 6
show(toInfix(exp2) + " = " + calc(exp2));// (1 + (2 * 3)) = 7
show(toInfix(exp3) + " = " + calc(exp3));// ((1 + 2) * 3) = 9

var exp4 = binop("+", binop("*", 3, 3), binop("*", 4, 4));
show(toInfix(exp4) + " = " + calc(exp4));// ((3 * 3) + (4 * 4)) = 25

var expError = binop("$", 2, 3);
show(calc(expError));    // 报错：不支持的操作 $
```

**【维加】**\
calc 可以不用定义帮助函数 calculator

**【SeaflyWechat】**\
好的，我改改：
```js
function calc(exp)
{
    if (! isBinOP(exp))
    {
        return isPair(exp)? first(exp):exp;
    }
    else
    {
        if (getOp(exp) == "+")
        {
            return calc(getE1(exp)) + calc(getE2(exp));
        }
        else if (getOp(exp) == "-")
        {
            return calc(getE1(exp)) - calc(getE2(exp));
        }
        else if (getOp(exp) == "*")
        {
            return calc(getE1(exp)) * calc(getE2(exp));
        }
        else if (getOp(exp) == "/")
        {
            return calc(getE1(exp)) / calc(getE2(exp));
        }
        else
        {
            throw "报错：不支持的操作 " + getOp(exp);
        }
    }
}
```

**【SeaflyWechat】**\



## 改变 binop 的实现
实现了计算器之后，请用类似之前的做法，使用 JavaScript 对象和数组的方式分别改变 binop 的实现，然后验证之前的代码全都正确运行。



# 个人总结

计算器基础模型:\
![[20210411220802528_29372.png]]

做题过程中所能想到的计算模型:\
![[20210411220828605_7152.png]]



