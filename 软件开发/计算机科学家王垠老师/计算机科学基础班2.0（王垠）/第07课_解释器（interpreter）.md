[TOC]

解释器是用来执行程序的机器。解释器可以是物理的机器（比如 CPU，GPU），也可以是运行在这种物理机器上的一个程序，甚至可以是运行在另一个解释器里面的程序。海龟的背上可以有海龟，上面还可以有海龟……



前面的练习里，我们写过一个计算器 calc。其实 calc 也是一个解释器，只是这个解释器缺少编程语言需要的「函数」，「调用」，「变量」等重要元素，所以通常被叫做“计算器”。现在有了所有需要的工具，我们就可以写一个完整的解释器了。



我们的新工具是查找结构（线性查找表和 BST）。查找结构实现的是数学里称为「映射」（map）的概念。给它一个 key，它就给我们相应的 value。



对照 addTable ～ addBST，lookupTable ～ lookupBST，你会发现线性查找表和 BST 的接口的本质一模一样。参数和返回值的数目，类型，作用都是一模一样的。在这个练习中，你会发现线性查找表和 BST 完全可以互换。我们可以把它们抽象出去，让解释器不知道它们的具体实现。在这里"不知道"意味着"不受约束"，意味着可以事后替换掉它。


# 数据类型

我们用跟以前一样的抽象设计，定义变量，函数，调用，闭包，binop 的构造函数和访问函数。其它几个都是已经学过的，只有闭包是这节课的新类型。

**闭包**就是函数的值。为什么要有闭包呢？回忆第一课的例子，var g = (x => y => x + y)(2)，我们得到 y => x + y 并让变量 g 指向它。但 y => x + y 并不是完整的信息，我们必须记住 x 等于 2，才能在 g(3) 调用时找到 x 的值。我们必须记住函数产生的时候（而不是调用的时候），函数体里面出现的**自由变量**（free variable）和它们的值。在 y => x + y 里面，x 就是自由变量，因为它不是这个函数里面的参数或变量。闭包就是用来记忆这个信息的。

闭包数据类型的两个成员分别是「函数」和「环境」。环境是一个查找结构，它记录了函数产生的位置所能"看见"的变量的值。

```js
// ---------- variable -----------
// 变量只有一个成员，就是它的名字。
function variable(name)
{
  return pair("variable", pair(name, null));
}

function isVariable(x)
{
  return isPair(x) && first(x) == "variable";
}

function variableName(v)
{
  return first(second(v));
}

// ---------- function -----------
// 为了简单，我们的函数只有一个参数。
// 函数的参数（param）是一个字符串（不是 variable）。
// 函数体（body）是一个任意的表达式。
function fun(param, body)
{
  return pair("function", pair(param, pair(body, null)));
}

function isFunction(x)
{
  return isPair(x) && first(x) == "function";
}

function funParam(f)
{
  return first(second(f));
}

function funBody(f)
{
  return first(second(second(f)));
}

// ---------- closure -----------
// 闭包的两个成员是：函数，函数产生时的环境。
function closure(fun, env)
{
  return pair("closure", pair(fun, pair(env, null)));
}

function isClosure(x)
{
  return isPair(x) && first(x) == "closure";
}

function closureFun(c)
{
  return first(second(c));
}

function closureEnv(c)
{
  return first(second(second(c)));
}

// ---------- call -----------
// 调用的第一个成员叫"操作符"（operator），第二个成员叫操作数（operand 或 argument）。
// 操作符可能是以下几种：
// 1. 函数表达式（匿名函数）
// 2. 指向函数的变量
// 3. 另一个调用，调用了返回函数的函数（比如 compose）
function call(op, arg)
{
  return pair("call", pair(op, pair(arg, null)));
}

function isCall(x)
{
  return isPair(x) && first(x) == "call";
}

function callOp(c)
{
  return first(second(c));
}

function callArg(c)
{
  return first(second(second(c)));
}

// ------------ binop -------------
function binop(op, e1, e2)
{
  return pair("binop", pair(op, pair(e1, pair(e2, null))));
}

function isBinOp(x)
{
  return isPair(x) && first(x) == "binop";
}

function binopOp(binop)
{
  return first(second(binop));
}

function binopE1(binop)
{
  return first(second(second(binop)));
}

function binopE2(binop)
{
  return first(second(second(second(binop))));
}

```

# 环境

有了这五种数据类型，我们还需要一个「环境」（environment）。环境记录了解释器能看到的变量的值，最初的环境是空的（emptyTable 或者 emptyBST）。调用发生的时候，环境会被扩展，产生新的环境，里面有参数对应的值。

当调用返回之后，参数会从环境里自动消失。为什么会自动消失呢？因为查找结构是函数式数据结构，只有调用内部的**递归解释器**才看得见新的环境。递归解释器返回之后，上一层的解释器只能看见原来的环境，里面没有这个参数的信息。函数式查找结构自然地实现了“参数只在函数内部可见”这个语言特征。

为了简单，我们先用线性查找表来表示环境。环境只需要定义三个变量，指向 emptyTable，addTable 和 lookupTable。
```js
var emptyEnv = emptyTable;
var extEnv = addTable;
var lookupEnv = lookupTable;
```

这是一种抽象。当你的解释器实现成功之后，只需要把这三个变量指向 BST 的实现，就能把环境变成 BST 结构，从而加快查找速度。

# expToString（把程序转换成字符串）

有了这些表示程序语言结构的数据类型，加上它们可以随意嵌套，再用 pairToString 或者 listToString 显示它们就不容易看明白了，所以在实现解释器之前，我们写一个 expToString 函数来把它转换成字符串。expToString 可以看作是 parser 的反函数。parser 把字符串转换成内部结构，expToString 把内部结构转换成字符串。

expToString 有着和解释器类似的构造，按照表达式的数据类型进行分支。你可以参考 pairToString 的思路来完成这个函数。
```js
function expToString(exp)
{
  if (typeof (exp) == "number"
        || typeof (exp) == "string") 
  {
    // TODO
  }
  else if (isVariable(exp))
  {
    // TODO
  }
  else if (isFunction(exp)) 
  {
    // TODO
  }
  else if (isCall(exp)) 
  {
    // TODO
  }
  else if (isBinOp(exp)) 
  {
    // TODO
  }
  else if (isClosure(exp))
  {
    // 闭包没有标准的显示方式，为了帮助理解，我们自己设计一个显示方式
    // 显示的内容是函数加上 env 的内容，中间加一个冒号 :
    // 函数需要递归调用 expToString，env 可以调用 listToString
  }
  else 
  {
    // 报错，非法表达式。
    throw "illegal expression";
  }
}

// 测试
test("test expToString variable",
     "x",
     expToString(variable("x")));

test("test expToString function",
     "x => x",
     expToString(fun("x", variable("x"))));

test("test expToString function with binop 1",
     "x => (x + 2)",
     expToString(fun("x", binop("+", variable("x"), 2))));
     
test("test expToString function with binop 2",
     "x => (1 + (x * 2))",
     expToString(fun("x", binop("+",
                                1,
                                binop("*", variable("x"), 2)))));

test("test expToString call op variable",
     "f(2)",
     expToString(call(variable("f"), 2)));
     
test("test expToString call nested",
     "f(g(2))",
     expToString(call(variable("f"), call(variable("g"), 2))));
     
test("test expToString curried call",
     "(x => y => (x + y))(2)(3)",
     expToString(
       call(
         call(
           fun("x",
               fun("y",
                   binop("+", variable("x"), variable("y")))),
           2),
         3)));
         
```


**【SeaflyWechat】**\
expToString 提交如下:
```js

function expToString(exp)
{
  if (typeof (exp) == "number"
        || typeof (exp) == "string") 
  {
    return String(exp);
  }
  else if (isVariable(exp))
  {
    return variableName(exp);
  }
  else if (isFunction(exp)) 
  {
    return expToString(funParam(exp)) 
        + " => " 
        + expToString(funBody(exp));
  }
  else if (isCall(exp)) 
  {
    if (isVariable(callOp(exp)))
    {
        return expToString(callOp(exp))
            + "("
            + expToString(callArg(exp))
            + ")";
    }
    else if (isFunction(callOp(exp)))
    {
        return "(" 
            + expToString(callOp(exp))
            + ")"
            + "("
            + expToString(callArg(exp))
            + ")";
    }
    else if (isCall(callOp(exp)))
    {
        return expToString(callOp(exp))
            + "("
            + expToString(callArg(exp))
            + ")";
    }
  }
  else if (isBinOp(exp)) 
  {
    return "("
        + expToString(binopE1(exp))
        + " "
        + expToString(binopOp(exp))
        + " "
        + expToString(binopE2(exp))
        + ")"
  }
  else if (isClosure(exp))
  {
    // 闭包没有标准的显示方式，为了帮助理解，我们自己设计一个显示方式
    // 显示的内容是函数加上 env 的内容，中间加一个冒号 :
    // 函数需要递归调用 expToString，env 可以调用 listToString
    return expToString(closureFun(exp))
        + " : "
        + expToString(closureEnv(exp));
  }
  else 
  {
    // 报错，非法表达式。
    throw "illegal expression";
  }
}
```

**【SeaflyWechat】**\
优化后的 expToString 如下:
```js
function expToString(exp)
{
  if (typeof (exp) == "number"
        || typeof (exp) == "string") 
  {
    return String(exp);
  }
  else if (isVariable(exp))
  {33
    return variableName(exp);
  }
  else if (isFunction(exp)) 
  {
    return expToString(funParam(exp)) 
        + " => " 
        + expToString(funBody(exp));
  }
  else if (isCall(exp)) 
  {
    if (isVariable(callOp(exp)) || isCall(callOp(exp)))
    {
        return expToString(callOp(exp))
            + "("
            + expToString(callArg(exp))
            + ")";
    }
    else //if (isFunction(callOp(exp)))
    {
        return "(" 
            + expToString(callOp(exp))
            + ")"
            + "("
            + expToString(callArg(exp))
            + ")";
    }
  }
  else if (isBinOp(exp)) 
  {
    return "("
        + expToString(binopE1(exp))
        + " "
        + expToString(binopOp(exp))
        + " "
        + expToString(binopE2(exp))
        + ")";
  }
  else if (isClosure(exp))
  {
    // 闭包没有标准的显示方式，为了帮助理解，我们自己设计一个显示方式
    // 显示的内容是函数加上 env 的内容，中间加一个冒号 :
    // 函数需要递归调用 expToString，env 可以调用 listToString
    return expToString(closureFun(exp))
        + " : "
        + expToString(closureEnv(exp));
  }
  else 
  {
    // 报错，非法表达式。
    throw "illegal expression";
  }
}
```








# 解释器

解释器就需要你自己写了。提供了一个比较详细的框架，这样不会毫无头绪。解释器比起 calc 多了一个参数 env，env 的起始值总是 emptyEnv。我们把双参数的解释器函数 interp 包在一个单参数的同名函数里面，这样使用者只需要给它一个表达式，而不需要知道 env 的存在。

我们的解释器功能虽少，却是完善的实现。因为具有 first-class function，它的能力跟 Scheme，Haskell 等语言的匿名函数部分相当，比 JavaScript 更加严谨。它能支持 compose 这样的高阶函数，可以把函数作为值任意传递使用。因为 compose(f, g) 本来应该接受两个参数，而我们的函数只能有一个参数，我们使用一种叫做 "currying" 的做法，也就是用 f => g => x => f(g(x))  这样的形式来模拟 (f, g) => x => f(g(x))。
```js
function interp(exp)
{
  function interp(exp, env)
  {
    if (typeof (exp) == "number"
      || typeof (exp) == "string") {
      // 输入是数字或字符串，返回它们自己。
    }
    else if (isVariable(exp)) {
      // 输入是变量，查找变量名字在 env 里的值。
      // 如果找不到就报错”未定义的变量：变量名字“。
    }
    else if (isFunction(exp)) {
      // 输入是函数，返回相应的闭包。
    }
    else if (isCall(exp)) {
      // 输入是调用。
      // 1. 首先对操作符，参数分别递归调用 interp 进行求值。
      // 2. 如果操作符的值是一个闭包，那么把闭包里保存的
      //    那个环境(closureEnv)取出来，扩展它，加入参数的值。
      //    然后把这个新环境用于对函数体求值(递归调用 interp)。
      // 3. 如果操作符部分的值不是一个闭包，那么报错”调用非函数“。
    }
    else if (isBinOp(exp)) {
      // 输入是二元操作，按照跟 calc 差不多的方式计算表达式的值。
      // 注意：为了避免产生依赖关系，请不要调用 calc。
    }
    else {
      // 报错，非法表达式。
      throw "illegal expression";
    }
  }

  return interp(exp, emptyEnv);
}


// 测试
show("------ interp ------");
test("test number", 42, interp(42));
test("test string", "good", interp("good"));

// ------- identity function --------
var idFun = fun("x", variable("x"));

test("test idFun text",
     "(closure (function x (variable x)) ())",
     listToString(interp(idFun)));

test("test identity function call",
     6,
     interp(call(idFun, 6)));

// ------- x => x * x --------
var sqFun = fun("x", binop("*", variable("x"), variable("x")));

test("test x => x * x text",
     "(closure (function x (binop * (variable x) (variable x))) ())",
     listToString(interp(sqFun)));

test("test x => x * x call",
     9,
     interp(call(sqFun, 3)));

// 显示 sqFun 的「表达式」的内部结构
show(expToString(sqFun));
// x => (x * x)

// 显示 sqFun 的「值」（闭包）的内部结构
show(expToString(interp(sqFun)));
// x => (x * x) : ()

// -------- curried add --------
// x => y => x + y 
var curriedAdd =
  fun("x",
      fun("y",
          binop("+", variable("x"), variable("y"))));

test("test curriedAdd",
     5,
     interp(call(call(curriedAdd, 2), 3)));

// 显示 curriedAdd(2) 返回的闭包的内部结构
// 根据是 table 还是 BST 稍有不同
show(expToString(interp(call(curriedAdd, 2))));
// table: y => (x + y) : ((x . 2))
// BST: y => (x + y) : (bst x 2 () ())

// --------- apply (curried) ---------
// f => x => f(x)
var applyFun =
  fun("f",
      fun("x",
          call(variable("f"), variable("x"))));

// apply(sqFun)(3)
test("test apply call",
     9,
     interp(call(call(applyFun, sqFun), 3)));

// -------- compose (curried) ---------
// f => g => x => f(g(x))
var composeFun =
  fun("f",
      fun("g",
          fun("x",
              call(variable("f"), call(variable("g"), variable("x"))))));

var add1 = fun("x", binop("+", variable("x"), 1));
var square = fun("x", binop("*", variable("x"), variable("x")));

// var composed = compose(add1)(square);
var composed1 = call(call(composeFun, add1), square);

// composed(3)
var composeCall1 = call(composed1, 3);
test("test composed call 1",
     10,
     interp(composeCall1));

// compose(square)(add1)(3)
var composeCall2 = call(call(call(composeFun, square), add1), 3);
test("test composed call 2",
     16,
     interp(composeCall2));

```


# 改进 1：用 BST 表示环境

把环境那三行代码换成 BST。看看测试，结果仍然正确。观察测试中显示的闭包数据结构发生了变化。
```js
var emptyEnv = emptyBST;
var extEnv = addBST;
var lookupEnv = lookupBST;
```



# 改进 2：实现条件分支

现在我们往解释器里加入条件分支。与 JavaScript 有所不同，我们的 if 是一个表达式，而不是一个语句，所以我们能在任何可以用表达式的地方使用 if。我们的设计是和 Scheme 语言的 if 一致的。另外，我们的 if 需要检查条件的值一定是 boolean 类型，而不是接受任何类型作为条件。这一点和 JavaScript 不同，也和 Scheme 不同。

比如，你可以在 Scheme 里写这样的程序：

```js
(define x (if (> 2 3) 1 2))
```
在 JavaScript 里，你不能这样使用 if，而必须使用"三元操作"（x? y : z）。其实 if 和三元操作的区别是没有必要的。

下面是 if 的数据类型定义：
```js
// --------- if ---------
function ifExp(condition, trueBranch, falseBranch)
{
  return pair("ifExp", pair(condition, pair(trueBranch, pair(falseBranch, null))));
}

function isIfExp(x)
{
  return isPair(x) && first(x) == "ifExp";
}

function ifCondition(ifexp)
{
  return first(second(ifexp));
}

function ifTrueBranch(ifexp)
{
  return first(second(second(ifexp)));
}

function ifFalseBranch(ifexp)
{
  return first(second(second(second(ifexp))));
}

```


请在解释器里加入 boolean 类型的常量 true 和 false，产生 boolean 类型的 binop 操作符：==, < 和 >，然后实现 if 语句。

```js
// ...
        else if (isIfExp(exp)) {
      // 先对条件表达式求值，检查条件的值一定是 boolean 类型。
      // 然后根据条件是 true 还是 false 决定执行哪一个分支。
    }
// ...


// 测试
// ---------- if -----------
test("if constant true",
     "cat",
     interp(ifExp(true, "cat", "dog")));

test("if constant false",
     "dog",
     interp(ifExp(false, "cat", "dog")));

test("test if binop true",
     "cat",
     interp(ifExp(binop("<", 1, 2), "cat", "dog")));

test("test if binop false",
     "dog",
     interp(ifExp(binop(">", 1, 2), "cat", "dog")));

test("test if fun true",
     "cat",
     interp(call(fun("f", ifExp(call(variable("f"), 12), "cat", "dog")),
                 fun("x", binop(">", variable("x"), 7)))));

test("test if fun false",
     "dog",
     interp(call(fun("f", ifExp(call(variable("f"), 5), "cat", "dog")),
                 fun("x", binop(">", variable("x"), 7)))));

// abs
var absExp =
  fun("x",
      ifExp(binop("<", variable("x"), 0),
            binop("-", 0, variable("x")),
            variable("x")));

test("test abs 1", 3, interp(call(absExp, 3)));
test("test abs 2", 7, interp(call(absExp, -7)));
test("test abs 3", 0, interp(call(absExp, 0)));

```



# 改进 3：用 Y combinator 实现递归函数

我们的解释器里没有定义变量的构造（类似 JavaScript 的 var），所以目前不能用普通的方式实现递归函数，但在这样简单的解释器里，你却可以用一种巧妙的办法实现递归函数。这种办法不需要使用 var 定义方式就能实现递归。

我们使用这样一个特殊的函数，叫「Y combinator」，它的定义如下。由于 Y combinator 理解起来比较复杂，目前你只需要拷贝它，不需要理解它是怎么回事。你可以在 JavaScript 里面实验下面的代码：

```js
// Y combinator 的定义
var Y = f =>
  (x => f(v => x(x)(v)))
  (x => f(v => x(x)(v)));
```

然后把 fact 函数写成下面的样子。把 fact 函数包在一个匿名函数 fact => ... 的函数体里面，然后把这个函数（起名叫 factGen） 交给  Y，你就得到跟 var（或者 function）定义的 fact 等价的递归函数。
```js
var factGen = fact =>
  n =>
  {
    if (n == 0)
    {
      return 1;
    }
    else
    {
      return n * fact(n - 1);
    }
  };

var yfact = Y(factGen);

show(yfact(5));
// 120
```

请注意，以上整个定义里没有使用递归函数定义（var 和 function 实现的功能）。factGen 里面出现了 fact 这个名字，但 fact 并不是 var 定义的变量，而是一个参数。虽然为了便于理解，用了 var 把 Y 和 factGen 分开定义，但其实也可以直接把 var 右边的表达式完全嵌入，就像下面这样，它会得到一样的结果。
```js
// 完全嵌入，不使用 var 也可以实现 fact
show("all in one fact(5): " +
  ((f =>
    (x => f(v => x(x)(v)))
    (x => f(v => x(x)(v))))

    (fact =>
      n =>
      {
        if (n == 0)
        {
          return 1;
        }
        else
        {
          return n * fact(n - 1);
        }
      })
  )(5)
);
```

现在我们可以在自己的语言里定义 Y combinator，然后用它实现上面这样的 fact 函数。请你把上面用 JavaScript 表示的 Y 和 factGen 翻译成我们自己的语言，起名为 YExp 和  factExp，然后 call(YExp, factGenExp) 就是 fact 函数了。
```js
var YExp = //TODO;
var factGenExp = //TODO;

// 用这个测试保证 YExp 翻译正确
test("test YExp to string",
     "f => (x => f(v => x(x)(v)))(x => f(v => x(x)(v)))",
     expToString(YExp)

var factExp = call(YExp, factGenExp);
test("test Y combinator 1", 120, interp(call(factExp, 5)));

// 完全去掉 var 的版本
show("all in one fact(5): " +
  interp(
  // TODO: 把 YExp 和 factExp 的内容完全嵌入这里，完全不使用 var
  )
)
```

Y combinator 为什么是那个样子？它是什么意思？稍后可能会讲。但现在可以开心的是，我们的解释器虽然不能定义 var 那样的变量，却是可以实现递归函数的。有了 Y combinator 的帮助，我们就具备了一个完整的语言，我们自己的语言已经可以实现课程中写过的几乎全部代码。


# 改进 4：let 局部变量

我们可以使用一种“let 表达式”来定义局部变量。这类似于 Scheme 语言的 let，却跟 JavaScript 的 var 有所不同。let 有明确的“作用区域”，而 var 的作用区域没有明显标出的界限（虽然还是有界限）。

在 Scheme 语言里，let 表达式是这样写的：
```scheme
(let ((x 2))
  (* x 3))
;; 得到 6

(let ((x 2)
      (y 3))
  (+ x y))
;; 得到 5
```

你可以看到，let 定义的变量有明确标出的作用区间（用括号分界）。每个 Scheme

的 let 可以同时“绑定”多个变量。

我们的语言为了简单，每个 let 表达式只定义一个新的变量。为了绑定多个变量，你可以使用嵌套的 let，像这样：
```scheme
(let ((x 2))
  (let ((y 3))
    (+ x y)))
;; 得到 5
```

let 表达式有 3 个组成部分：name，value，body。let 会把 name 绑定于 value，然后你就可以在 body 里访问到 name。

下面是 let 的测试，你可以从中理解一下它的用法。
```js
show("-------- let ---------");

// (let ((x 2))
//    x)
var let1 = letExp("x", 2, variable("x"));
test("test let 1", 2, interp(let1));

// (let ((x (* 2 3)))
//   x)
var let1a = letExp("x",
                   binop("*", 2, 3),
                   variable("x"));

test("test let 2", 6, interp(let1a));

// (let ((x 2))
//    (* x 3))
var let2 = letExp("x", 2, binop("*", variable("x"), 3));
test("test let 3", 6, interp(let2));

// Scheme 代码：
// (let ((x 2))
//  (let ((y 3))
//    (+ x y))
var let3 = letExp("x", 2,
                  letExp("y", 3,
                         binop("+", variable("x"), variable("y"))));

test("test nested let", 5, interp(let3));

var let4 = letExp("f", fun("x", variable("x")),
                  call(variable("f"), 42));
                  
test("test let 4",
     42,
     interp(let4));
```


我提供给你 let 的构造函数，类型判断函数和访问函数：
```js
function letExp(name, value, body)
{
  return pair("let", pair(name, pair(value, pair(body, null))));
}

function isLet(x)
{
  return isPair(x) && first(x) == "let";
}

function letName(l)
{
  return first(second(l));
}

function letValue(l)
{
  return first(second(second(l)));
}

function letBody(l)
{
  return first(second(second(second(l))));
}
```

现在请你把 let 添加到解释器里，并且让示例得出正确的结果。

**思考题**：let 其实可以被看作是匿名函数调用的“语法糖”（syntactic sugar）。下面两个 Scheme 代码是等价的：

```scheme
(let ((x value))
  body)

((lambda (x) body)
 value)
```

请思考一下为什么，并且利用这个等价性，在解释器里做出另外一种对 let 的实现。



# 计算机科学基础班2.0

**【计算机科学家王垠老师ian】**\
Y comb的PPT链接：https://yinwang0.wordpress.com/2012/04/09/reinvent-y/

**【计算机科学家王垠老师ian】**\
逻辑表达公式:\
![[20210411221346296_25102.png]]

**【计算机科学家王垠老师ian】**\
思考题：这个逻辑学公式，里面 ```<:``` 对应我们代码里的 ```subtype``` 函数，那么中间那个长的横线对应着什么呢？中间那根最长的横线。

**【计算机科学家王垠老师ian】**\
昨天讲的 Cat[] 和 Animal[] 的子类型问题，其实可以用泛型解决。

**【计算机科学家王垠老师ian】**\
有时候不能把 Cat[] 传给 Animal[] 是一件不方便的事情。比如，你如果想把一个数组里的动物顺序掉一个头，却发现 Cat[] 不能传进去。

**【计算机科学家王垠老师ian】**\
其实这个时候你根本不关心数组里面是什么，但就算你的参数是 Object[] 也不能把 Cat[] 传进去。就麻烦了。

**【秋天的风】**\
哦，是不是要加一个标记明确表示可以传子类型进去。

**【计算机科学家王垠老师ian】**\
不是的。这些类型系统里面一切都有原因的，不是设计者规定可以怎么就可以怎么。

**【秋天的风】**\
真没想到会这么不简单。

**【计算机科学家王垠老师ian】**\
本来应该是简单的，但其实研究了一百多年了吧

**【大蔡】**\
一百多年，呢么久了

**【计算机科学家王垠老师ian】**\
其实是逻辑学的内容, 还没有计算机的时候就已经在研究了, 这些很容易就变成理发师悖论之类的, 然后就回到希尔伯特的年代去了


