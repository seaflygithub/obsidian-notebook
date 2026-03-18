
var show = (x) => console.log(x);

var pi = 3.14159;
function innerArea(a, b)
{
    var fc = (a,b) => Math.sqrt(a * a + b * b) / 2;
    var fs = r => pi * r * r;
    return fs(fc(a,b));
}
//show(innerArea(3, 4));//19.6349375

//举个例子:two(add1)(0)，相当于 add1(add1(0))，会返回 2。two(square)(3)，相当于 square(square(3))，会返回 81
var two = (f) => ((x) => f(f(x)))
var add1 = (x) => x + 1;
var square = (x) => x * x;
// show(two(add1)(0));//2
// show(two(square)(3));//81

var three = (f) => ((x) => f(f(f(x))))
var four = (f) => ((x) => f(f(f(f(x)))))
// show(three(add1)(0));//3
// show(three(square)(3));//6561
// show(four(square)(3));//43046721

var succ = (n) => (f) => (x) => f(n(f)(x));
var three = succ(two);
// show(three(square)(3));//6561

function compose(f, g)
{
  return x => f(g(x));
}
var two = f => compose(f, f);
//用 compose 来改写 succ
//提示：用 compose 改写之后，也许可以利用一个等价关系来简化它。
//如果 f 是一个单参数的函数，那么 x => f(x) 等价于 f。
//先想一下这是为什么？如果 f 是多参数的函数，也有类似的等价关系，比如 (x, y) => f(x, y) 等价于 f。
var succ = n => f => compose(f, n(f));
var three = succ(two);
// show(three(square)(3));//6561

function toNumber(n)
{
    return n(add1)(0);
}
// show(toNumber(two)); //返回 2
// show(toNumber(three)); //返回 3
// show(toNumber(four)); //返回 4

var zero = f => x => x;
var one = succ(zero);
var two = succ(one);
var three = succ(two);
var four = succ(three);
var five = succ(four);
var six = succ(five);
var seven = succ(six);
var eight = succ(seven);
var nine = succ(eight);
var ten = succ(nine);
// show(toNumber(one));
// show(toNumber(two));
// show(toNumber(three));
// show(toNumber(four));
// show(toNumber(five));
// show(toNumber(six));
// show(toNumber(seven));
// show(toNumber(eight));
// show(toNumber(nine));
// show(toNumber(ten));

function plus(m, n)
{
    return f => compose(m(f), n(f));
    return f => x => n(f)(m(f)(x));
}
// show(toNumber(plus(two, three))); //会返回 5
// show(toNumber(plus(five, six))); //会返回 11

function mult(m, n)
{
    return f => x => m(n(f))(x);
}
// show(toNumber(mult(two, three))); //会返回 6
// show(toNumber(mult(five, six))); //会返回 30

function mult(m, n)
{
    return compose(m, n); //x => f(g(x)) ==> m(n(f))
}
var mult = compose;
// show(toNumber(mult(two, three))); //会返回 6
// show(toNumber(mult(five, six))); //会返回 30

function pow(m, n)
{
    return n(m);
}
// show(toNumber(pow(two, three))); //会返回 8
// show(toNumber(pow(five, six))); //会返回 15625